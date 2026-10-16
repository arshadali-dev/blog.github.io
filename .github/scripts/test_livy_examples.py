"""Offline contract tests; these never contact Fabric."""

import ast
from contextlib import redirect_stdout
from io import StringIO
import json
import unittest
from unittest.mock import Mock, patch

import requests
from azure.core.exceptions import ClientAuthenticationError

import sync_livy_examples as source


def helpers(filename="livy_quickstart.py"):
    tree = ast.parse((source.DESTINATION / filename).read_text(encoding="utf-8"))
    tree.body = [
        node for node in tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef))
    ]
    namespace = {
        "BASE_URL": "https://example.invalid/livy",
        "TOKEN_SCOPE": "https://api.fabric.microsoft.com/.default",
        "credential": Mock(),
        "spark_conf": {},
    }
    namespace["credential"].get_token.return_value.token = "test-token"
    exec(compile(tree, filename, "exec"), namespace)
    return namespace


class Downloads(unittest.TestCase):
    def test_generated_files_and_zip_are_current(self):
        for name, content in source.expected_files().items():
            with self.subTest(name=name):
                self.assertEqual((source.DESTINATION / name).read_bytes(), content)

    def test_quality_query_matches_the_article(self):
        post = source.POST.read_text(encoding="utf-8")
        blocks = source.python_blocks(
            source.section(post, "Optional: Check Lakehouse Data Quality")
        )
        self.assertEqual(len(blocks), 1)
        self.assertIn(blocks[0].strip(), source.QUALITY_BODY)

    def test_shared_helpers_match_in_all_clients(self):
        reference = ast.parse(
            (source.DESTINATION / "livy_quickstart.py").read_text(encoding="utf-8")
        )
        expected = {
            node.name: ast.dump(node)
            for node in reference.body
            if isinstance(node, ast.FunctionDef)
        }
        for path in source.DESTINATION.glob("*.py"):
            if path.name == "livy_range_job.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            actual = {
                node.name: ast.dump(node)
                for node in tree.body
                if isinstance(node, ast.FunctionDef)
            }
            for name in ("api", "wait_for", "release"):
                with self.subTest(file=path.name, helper=name):
                    self.assertEqual(actual[name], expected[name])


class Helpers(unittest.TestCase):
    def setUp(self):
        self.ns = helpers()

    def test_authenticated_requests_have_finite_timeouts(self):
        response = Mock(content=b'{"id": 1}')
        response.json.return_value = {"id": 1}
        with patch("requests.request", return_value=response) as request:
            self.assertEqual(self.ns["api"]("POST", "/sessions", {}), {"id": 1})
        self.assertEqual(request.call_args.kwargs["timeout"], (10, 60))
        self.assertEqual(
            request.call_args.kwargs["headers"]["Authorization"], "Bearer test-token"
        )
        response.raise_for_status.assert_called_once()

    def test_only_delete_404_is_accepted(self):
        for method, status in (("DELETE", 404), ("GET", 404), ("DELETE", 403)):
            with self.subTest(method=method, status=status):
                response = requests.Response()
                response.status_code = status
                with patch("requests.request", return_value=response):
                    if method == "DELETE" and status == 404:
                        self.assertIsNone(self.ns["api"](method, "/sessions/1"))
                    else:
                        with self.assertRaises(requests.HTTPError):
                            self.ns["api"](method, "/sessions/1")

    def test_wait_normalizes_state_and_stops_at_deadline(self):
        self.ns["api"] = Mock(return_value={"state": "Idle"})
        self.assertEqual(self.ns["wait_for"]("/sessions/1", "idle")["state"], "Idle")
        with patch("time.monotonic", side_effect=[0, 901]):
            with self.assertRaises(TimeoutError):
                self.ns["wait_for"]("/sessions/1", "idle")

    def test_wait_rejects_terminal_states(self):
        for state in ("Error", "Dead", "Killed", "Failed", "Cancelled", "Shutting_Down"):
            self.ns["api"] = Mock(return_value={"state": state})
            with self.subTest(state=state), self.assertRaises(RuntimeError):
                self.ns["wait_for"]("/sessions/1", "idle")

    def test_transport_errors_are_not_retried(self):
        self.ns["api"] = Mock(side_effect=requests.Timeout("connection lost"))
        with self.assertRaises(requests.Timeout):
            self.ns["wait_for"]("/sessions/1", "idle")
        self.ns["api"].assert_called_once()

    def test_available_is_not_spark_success(self):
        self.ns["api"] = Mock(return_value={"id": 1})
        self.ns["wait_for"] = Mock(
            return_value={"state": "available", "output": {"status": "error"}}
        )
        with self.assertRaisesRegex(RuntimeError, "Spark execution failed"):
            self.ns["run_code"]("/sessions/1/statements", "bad_code")

    def test_cleanup_failure_is_raised_without_execution_failure(self):
        for error in (requests.Timeout("DELETE timed out"),
                      ClientAuthenticationError("token unavailable")):
            self.ns["api"] = Mock(side_effect=error)
            with self.subTest(error=type(error).__name__), self.assertRaises(type(error)):
                self.ns["release"]("/sessions/1")

    def test_cleanup_failure_preserves_original_error_with_note(self):
        original = RuntimeError("Spark failed")
        self.ns["api"] = Mock(side_effect=requests.HTTPError("DELETE forbidden"))
        try:
            try:
                raise original
            finally:
                self.ns["release"]("/sessions/1")
        except RuntimeError as error:
            self.assertIs(error, original)
            self.assertIn("DELETE forbidden", error.__notes__[0])


class StandaloneClients(unittest.TestCase):
    def run_client(self, name, failure=None):
        calls = []
        statements = {}

        def request(method, url, **kwargs):
            path = url.split("/2023-12-01", 1)[1]
            payload = kwargs.get("json")
            calls.append((method, path, payload))
            status = 200
            if method == "DELETE":
                status = 500 if failure == "cleanup" else 404
                body = {"error": "cleanup failed"} if status == 500 else {}
            elif path.endswith("/statements") and method == "POST":
                statement_id = len(statements) + 1
                statements[statement_id] = payload
                body = {"id": statement_id}
            elif "/statements/" in path:
                submitted = statements[int(path.rsplit("/", 1)[-1])]
                if failure == "spark":
                    output = {"status": "error", "evalue": "example error"}
                elif submitted["kind"] == "sql":
                    output = {"status": "ok", "data": {"application/json": {
                        "schema": {"fields": [{"name": "result"}]},
                        "data": [[1]], "truncated": failure == "truncated",
                    }}}
                else:
                    text = '[{"id": 1}, {"id": 2}, {"id": 3}]' if "json.dumps" in submitted["code"] else "3"
                    output = {"status": "ok", "data": {"text/plain": text}}
                body = {"state": "available", "output": output}
            elif method == "POST":
                body = {"id": 1}
            elif failure == "startup":
                body = {"state": "Failed"}
            elif path.startswith("/batches/"):
                body = {"state": "success"}
            else:
                body = {"state": "Idle", "sessionId": 10, "replId": 20}
            response = requests.Response()
            response.status_code = status
            response._content = json.dumps(body).encode()
            response.url = url
            return response

        code = (source.DESTINATION / name).read_text(encoding="utf-8")
        output = StringIO()
        try:
            with patch("azure.identity.AzureCliCredential") as credential, \
                    patch("requests.request", side_effect=request), \
                    redirect_stdout(output):
                credential.return_value.get_token.return_value.token = "test-token"
                exec(compile(code, name, "exec"), {"__name__": "__main__"})
        finally:
            self.calls = calls
            self.output = output.getvalue()

    def test_all_basic_downloads_execute_and_delete_their_resources(self):
        for name in ("livy_quickstart.py", "livy_sql_demo.py",
                     "livy_environment_demo.py", "submit_livy_batch.py", "livy_hc_demo.py"):
            with self.subTest(name=name):
                self.run_client(name)
                self.assertEqual(self.calls[-1][0], "DELETE")
                self.assertTrue(self.output.strip())

    def test_environment_is_serialized_only_in_creation_payload(self):
        self.run_client("livy_environment_demo.py")
        self.assertEqual(
            json.loads(self.calls[0][2]["conf"]["spark.fabric.environmentDetails"]),
            {"id": "<environment-id>"},
        )
        statement = next(payload for method, path, payload in self.calls if method == "POST" and path.endswith("/statements"))
        self.assertNotIn("conf", statement)

    def test_optional_environment_is_omitted_by_default(self):
        for name in ("submit_livy_batch.py", "livy_hc_demo.py"):
            with self.subTest(name=name):
                self.run_client(name)
                self.assertNotIn("spark.fabric.environmentDetails", self.calls[0][2]["conf"])

    def test_startup_failure_still_requests_cleanup(self):
        for name in ("livy_quickstart.py", "livy_environment_demo.py",
                     "submit_livy_batch.py", "livy_hc_demo.py"):
            with self.subTest(name=name), self.assertRaisesRegex(RuntimeError, "Execution failed"):
                self.run_client(name, failure="startup")
            self.assertEqual(self.calls[-1][0], "DELETE")

    def test_sql_error_and_truncation_still_request_cleanup(self):
        for failure in ("spark", "truncated"):
            for name in ("livy_sql_demo.py", "livy_environment_demo.py"):
                with self.subTest(name=name, failure=failure), self.assertRaises(RuntimeError):
                    self.run_client(name, failure=failure)
                self.assertEqual(self.calls[-1][0], "DELETE")

    def test_cleanup_failure_is_not_reported_as_success(self):
        with self.assertRaises(requests.HTTPError):
            self.run_client("livy_quickstart.py", failure="cleanup")


class TwoContexts(unittest.TestCase):
    def run_example(self, failure=None, packed=True):
        ns = helpers()
        events = []
        contexts = 0
        statement_counts = {}

        def api(method, path, payload=None):
            nonlocal contexts
            events.append((method, path))
            if method == "POST" and path == "/highConcurrencySessions":
                contexts += 1
                if failure == "acquire" and contexts == 2:
                    raise requests.HTTPError("Second acquisition failed")
                return {"id": contexts}
            if method == "POST":
                count = statement_counts.get(path, 0) + 1
                statement_counts[path] = count
                return {"id": count}
            if method == "DELETE" and failure in ("cleanup", "both"):
                raise requests.HTTPError(f"Could not delete {path}")
            return None

        def wait_for(path, target):
            events.append(("WAIT", path))
            if target == "idle":
                context_id = int(path.rsplit("/", 1)[-1])
                return {"sessionId": 10 if packed else context_id, "replId": context_id}
            if failure in ("execute", "both"):
                return {"output": {"status": "error"}}
            label = "A" if "/repls/1/" in path else "B"
            text = "A" if path.endswith("/statements/2") else f"{label} 3"
            return {"output": {"status": "ok", "data": {"text/plain": text}}}

        ns["api"] = api
        ns["wait_for"] = wait_for
        output = StringIO()
        try:
            with redirect_stdout(output):
                exec(source.TWO_CONTEXT_BODY, ns)
        finally:
            self.events = events
            self.output = output.getvalue()

    def test_both_jobs_submitted_before_polling_and_both_released(self):
        self.run_example()
        first_wait = next(
            i for i, (method, path) in enumerate(self.events)
            if method == "WAIT" and "/statements/" in path
        )
        submissions = [
            event for event in self.events[:first_wait]
            if event[0] == "POST" and event[1].endswith("/statements")
        ]
        self.assertEqual(len(submissions), 2)
        self.assertEqual(sum(method == "DELETE" for method, _ in self.events), 2)
        self.assertIn("Shared Spark session: True", self.output)
        self.assertIn("REPL A marker after both jobs: A", self.output)

    def test_different_sessions_are_reported_honestly(self):
        self.run_example(packed=False)
        self.assertIn("Packing was not observed", self.output)

    def test_partial_acquisition_releases_first_context(self):
        with self.assertRaisesRegex(requests.HTTPError, "Second acquisition"):
            self.run_example(failure="acquire")
        self.assertIn(("DELETE", "/highConcurrencySessions/1"), self.events)

    def test_cleanup_attempts_every_context_and_reports_all_failures(self):
        with self.assertRaises(ExceptionGroup) as result:
            self.run_example(failure="cleanup")
        self.assertEqual(len(result.exception.exceptions), 2)
        self.assertEqual(sum(method == "DELETE" for method, _ in self.events), 2)

    def test_execution_error_retained_when_both_cleanups_fail(self):
        with self.assertRaisesRegex(RuntimeError, "Spark execution failed") as result:
            self.run_example(failure="both")
        self.assertEqual(len(result.exception.__notes__), 2)
        self.assertEqual(sum(method == "DELETE" for method, _ in self.events), 2)


class DataQuality(unittest.TestCase):
    def run_example(self, *, truncated=False, spark_error=False, cleanup_error=False, values=None):
        ns = helpers()
        ns["api"] = Mock(side_effect=[{"id": 1}, {"id": 2}, None])
        output = {
            "status": "error" if spark_error else "ok",
            "data": {"application/json": {
                "schema": {"fields": [
                    {"name": "row_count", "type": "long"},
                    {"name": "null_customer_count", "type": "long"},
                ]},
                "data": [values if values is not None else ["3", "1"]],
                "truncated": truncated,
            }},
        }
        ns["wait_for"] = Mock(side_effect=[{"state": "idle"}, {"output": output}])
        ns["run_code"] = Mock(side_effect=[
            "", requests.HTTPError("DROP failed") if cleanup_error else "",
        ])
        captured = StringIO()
        try:
            with redirect_stdout(captured):
                exec(source.QUALITY_BODY, ns)
        finally:
            self.ns = ns
            self.output = captured.getvalue()

    def test_partitioned_fixture_is_cleaned_and_metrics_checked(self):
        self.run_example()
        query = self.ns["api"].call_args_list[1].args[2]["code"]
        self.assertIn("WHERE order_date = DATE '2026-10-01'", query)
        self.assertIn("COUNT(*) AS row_count", query)
        self.assertIn("DROP TABLE IF EXISTS fact_orders_livy_", self.ns["run_code"].call_args.args[1])
        self.ns["api"].assert_called_with("DELETE", "/sessions/1")
        self.assertIn("{'row_count': 3, 'null_customer_count': 1}", self.output)

    def test_integer_counts_are_also_supported(self):
        self.run_example(values=[3, 1])
        self.assertIn("{'row_count': 3, 'null_customer_count': 1}", self.output)

    def test_invalid_count_is_not_silently_replaced(self):
        with self.assertRaises(ValueError):
            self.run_example(values=["not-a-number", "1"])
        self.ns["api"].assert_called_with("DELETE", "/sessions/1")

    def test_truncated_result_still_cleans_up(self):
        with self.assertRaisesRegex(RuntimeError, "truncated"):
            self.run_example(truncated=True)
        self.assertEqual(self.ns["run_code"].call_count, 2)
        self.ns["api"].assert_called_with("DELETE", "/sessions/1")

    def test_fixture_cleanup_does_not_mask_spark_error(self):
        with self.assertRaisesRegex(RuntimeError, "Spark SQL execution failed") as result:
            self.run_example(spark_error=True, cleanup_error=True)
        self.assertIn("DROP failed", result.exception.__notes__[0])
        self.ns["api"].assert_called_with("DELETE", "/sessions/1")


if __name__ == "__main__":
    unittest.main()
