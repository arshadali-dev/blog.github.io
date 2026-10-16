# Python 3.11+. Replace the ID placeholders before running.
import json
import sys
import time
import requests
from azure.core.exceptions import AzureError
from azure.identity import AzureCliCredential

TENANT_ID = "<tenant-id>"
WORKSPACE_ID = "<workspace-id>"
LAKEHOUSE_ID = "<lakehouse-id>"

BASE_URL = (
    f"https://api.fabric.microsoft.com/v1/workspaces/{WORKSPACE_ID}"
    f"/lakehouses/{LAKEHOUSE_ID}/livyapi/versions/2023-12-01"
)
TOKEN_SCOPE = "https://api.fabric.microsoft.com/.default"
credential = AzureCliCredential(tenant_id=TENANT_ID)
spark_conf = {}


def api(method, path, payload=None):
    token = credential.get_token(TOKEN_SCOPE).token
    response = requests.request(
        method,
        BASE_URL + path,
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=(10, 60),
    )
    if method == "DELETE" and response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json() if response.content else None


def wait_for(path, target, timeout=900):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        item = api("GET", path)
        state = item["state"].lower()
        if state == target:
            return item
        if state in {"error", "dead", "killed", "failed", "cancelled", "shutting_down"}:
            raise RuntimeError(f"Execution failed at {path}: {item}")
        time.sleep(2)
    raise TimeoutError(f"Timed out waiting for {target} at {path}")


def run_code(statements_path, code):
    statement = api("POST", statements_path, {"code": code, "kind": "pyspark"})
    path = f"{statements_path}/{statement['id']}"
    completed = wait_for(path, "available")
    output = completed["output"]
    if output["status"] != "ok":
        raise RuntimeError(f"Spark execution failed: {output}")
    return output["data"]["text/plain"]


def release(path):
    execution_error = sys.exception()
    try:
        api("DELETE", path)
    except (requests.RequestException, AzureError) as cleanup_error:
        if execution_error is None:
            raise
        execution_error.add_note(
            f"Cleanup also failed for {path}: {cleanup_error}. "
            "Check Fabric and release the resource."
        )


from uuid import uuid4

SESSION_TAG = f"livy-blog-two-{uuid4().hex}"
spark_conf["spark.highConcurrency.max"] = "4"


def read_result(statement_path):
    completed = wait_for(statement_path, "available")
    output = completed["output"]
    if output["status"] != "ok":
        raise RuntimeError(f"Spark execution failed: {output}")
    return output["data"]["text/plain"].strip()


context_paths = []
contexts = []
try:
    # Wait for the first context before acquiring the second to favor packing.
    for label in ("A", "B"):
        context = api("POST", "/highConcurrencySessions", {
            "sessionTag": SESSION_TAG,
            "conf": spark_conf,
        })
        path = f"/highConcurrencySessions/{context['id']}"
        context_paths.append(path)
        ready = wait_for(path, "idle")
        statements = (
            f"/highConcurrencySessions/{ready['sessionId']}"
            f"/repls/{ready['replId']}/statements"
        )
        contexts.append((label, ready, statements))
        print(label, "HC ID:", context["id"],
              "sessionId:", ready["sessionId"], "replId:", ready["replId"])

    packed = contexts[0][1]["sessionId"] == contexts[1][1]["sessionId"]
    print("Shared Spark session:", packed)
    if not packed:
        print("Packing was not observed; Fabric allocated separate sessions.")

    submitted = []
    for label, _, statements in contexts:
        statement = api("POST", statements, {
            "kind": "pyspark",
            "code": (
                f"marker = {label!r}\n"
                "print(marker, spark.range(1, 4).count())"
            ),
        })
        submitted.append((label, f"{statements}/{statement['id']}"))
    print("Both statements submitted; now waiting for their results.")

    for label, statement_path in submitted:
        result = read_result(statement_path)
        print("Result:", result)
        if result != f"{label} 3":
            raise RuntimeError(f"Unexpected result for {label}: {result}")

    statements_a = contexts[0][2]
    probe = api("POST", statements_a, {
        "kind": "pyspark", "code": "print(marker)",
    })
    marker_a = read_result(f"{statements_a}/{probe['id']}")
    print("REPL A marker after both jobs:", marker_a)
    if marker_a != "A":
        raise RuntimeError(f"Unexpected REPL A state: {marker_a}")
finally:
    cleanup_errors = []
    for path in reversed(context_paths):
        try:
            release(path)
        except (requests.RequestException, AzureError) as error:
            cleanup_errors.append(error)
    if cleanup_errors:
        raise ExceptionGroup("Could not release all HC contexts", cleanup_errors)
