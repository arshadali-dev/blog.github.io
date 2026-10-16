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
ENVIRONMENT_ID = "<environment-id>"

BASE_URL = (
    f"https://api.fabric.microsoft.com/v1/workspaces/{WORKSPACE_ID}"
    f"/lakehouses/{LAKEHOUSE_ID}/livyapi/versions/2023-12-01"
)
TOKEN_SCOPE = "https://api.fabric.microsoft.com/.default"
credential = AzureCliCredential(tenant_id=TENANT_ID)
spark_conf = {
    "spark.fabric.environmentDetails": json.dumps({"id": ENVIRONMENT_ID})
}


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


session = api("POST", "/sessions", {"conf": spark_conf})
session_path = f"/sessions/{session['id']}"
try:
    wait_for(session_path, "idle")
    statement = api("POST", f"{session_path}/statements", {
        "kind": "sql",
        "code": "SELECT 1 AS result",
    })
    statement_path = f"{session_path}/statements/{statement['id']}"
    completed = wait_for(statement_path, "available")
    output = completed["output"]
    if output["status"] != "ok":
        raise RuntimeError(f"SQL execution failed: {output}")

    table = output["data"]["application/json"]
    if table["truncated"]:
        raise RuntimeError("SQL result was truncated; reduce the result size.")
    print("Columns:", [field["name"] for field in table["schema"]["fields"]])
    print("Rows:", table["data"])
finally:
    release(session_path)
