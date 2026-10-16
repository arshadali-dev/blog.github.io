"""Generate standalone downloads from the blog and the two advanced examples."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
import re
import zipfile
from io import BytesIO

ROOT = Path(__file__).resolve().parents[2]
POST = ROOT / "_posts" / "2026-10-15-fabric-spark-livy-api.md"
DESTINATION = ROOT / "assets" / "downloads" / "fabric-livy"
HEADER = "# Python 3.11+. Replace the ID placeholders before running.\n"

QUALITY_BODY = '''
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
'''.strip()

TWO_CONTEXT_BODY = '''
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
                f"marker = {label!r}\\n"
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
'''.strip()


def python_blocks(section: str) -> list[str]:
    return re.findall(r"^```python\n(.*?)^```", section, re.MULTILINE | re.DOTALL)


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise ValueError(f"Missing blog section: {heading}")
    return match.group(1)


def expected_files() -> dict[str, bytes]:
    text = POST.read_text(encoding="utf-8")
    setup = python_blocks(section(text, "1. Sign In and Set the Lakehouse"))
    helpers = python_blocks(section(text, "2. Add Small REST Helpers"))
    if len(setup) != 1 or len(helpers) != 4:
        raise ValueError("Expected one setup block and four helper blocks.")
    common = setup + helpers
    bodies = {
        "livy_quickstart.py": common + python_blocks(
            section(text, "3. Run PySpark and Spark SQL")
        ),
        "livy_sql_demo.py": common + python_blocks(
            section(text, 'Submit Spark SQL Directly with `kind: "sql"`')
        ),
        "livy_environment_demo.py": python_blocks(
            section(text, "Optional: Attach a Fabric Environment")
        ),
        "livy_hc_demo.py": python_blocks(
            section(text, "Optional: Use High Concurrency")
        ),
        "livy_quality_demo.py": common + [QUALITY_BODY],
        "livy_hc_two_contexts.py": common + [TWO_CONTEXT_BODY],
    }
    batch = python_blocks(section(text, "Optional: Submit a Batch Job"))
    if len(batch) != 2:
        raise ValueError("Expected remote script and local batch client.")
    bodies["livy_range_job.py"] = [batch[0]]
    bodies["submit_livy_batch.py"] = [batch[1]]
    files = {}
    for name, blocks in bodies.items():
        header = (
            "# Runs on Fabric Spark. Upload to OneLake; pass the output path as argv[1].\n"
            if name == "livy_range_job.py" else HEADER
        )
        content = header + "\n\n\n".join(block.strip() for block in blocks) + "\n"
        ast.parse(content, filename=name)
        files[name] = content.encode("utf-8")
    files["requirements.txt"] = (
        "# Client packages used for the validation recorded in the blog.\n"
        "azure-identity==1.25.3\nazure-core==1.39.0\nrequests==2.33.1\n"
    ).encode("utf-8")
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)
    files["fabric-livy-examples.zip"] = buffer.getvalue()
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail on stale downloads.")
    args = parser.parse_args()
    for name, content in expected_files().items():
        path = DESTINATION / name
        if args.check:
            if not path.exists() or path.read_bytes() != content:
                raise SystemExit(f"Out-of-date download: {path}")
        else:
            DESTINATION.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print("Livy downloads match their source." if args.check else "Generated Livy downloads.")


if __name__ == "__main__":
    main()
