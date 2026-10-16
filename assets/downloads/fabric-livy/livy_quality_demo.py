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

table_name = f"fact_orders_livy_{uuid4().hex}"
create_query = f"""
CREATE TABLE {table_name}
USING DELTA
PARTITIONED BY (order_date)
AS SELECT * FROM VALUES
    (1, CAST(101 AS BIGINT), DATE '2026-10-01'),
    (2, CAST(NULL AS BIGINT), DATE '2026-10-01'),
    (3, CAST(103 AS BIGINT), DATE '2026-10-01'),
    (4, CAST(104 AS BIGINT), DATE '2026-10-02')
AS orders(order_id, customer_id, order_date)
"""
quality_query = f"""
SELECT
    COUNT(*) AS row_count,
    COALESCE(SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END), 0)
        AS null_customer_count
FROM {table_name}
WHERE order_date = DATE '2026-10-01'
"""


def drop_fixture(statements):
    execution_error = sys.exception()
    try:
        run_code(statements, f"spark.sql('DROP TABLE IF EXISTS {table_name}')")
    except (requests.RequestException, AzureError, RuntimeError, TimeoutError) as error:
        if execution_error is None:
            raise
        execution_error.add_note(
            f"Could not remove demonstration table {table_name}: {error}. "
            "Check Fabric and remove only this generated table."
        )


print("Demonstration table:", table_name)
session = api("POST", "/sessions", {"conf": spark_conf})
session_path = f"/sessions/{session['id']}"
fixture_submitted = False
try:
    wait_for(session_path, "idle")
    statements = f"{session_path}/statements"
    fixture_submitted = True
    run_code(statements, f"spark.sql({create_query!r})")
    statement = api("POST", statements, {"kind": "sql", "code": quality_query})
    completed = wait_for(f"{statements}/{statement['id']}", "available")
    output = completed["output"]
    if output["status"] != "ok":
        raise RuntimeError(f"Spark SQL execution failed: {output}")
    table = output["data"]["application/json"]
    if table["truncated"]:
        raise RuntimeError("Quality result was truncated.")
    columns = [field["name"] for field in table["schema"]["fields"]]
    if len(table["data"]) != 1 or len(columns) != len(table["data"][0]):
        raise RuntimeError(f"Unexpected quality result shape: {table}")
    values = dict(zip(columns, table["data"][0]))
    result = {
        "row_count": int(values["row_count"]),
        "null_customer_count": int(values["null_customer_count"]),
    }
    print("Quality result:", result)
    if result != {"row_count": 3, "null_customer_count": 1}:
        raise RuntimeError(f"Unexpected demonstration result: {result}")
    print("Quality check: REVIEW - 1 order has no customer ID.")
finally:
    try:
        if fixture_submitted:
            drop_fixture(statements)
    finally:
        release(session_path)
