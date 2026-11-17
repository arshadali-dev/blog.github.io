"""Offline SQL notebook contract tests; no Spark or Fabric execution."""

import hashlib
import json
import re
import sqlite3
import unittest

import sync_pipe_notebook as shared
import sync_sql_notebook as source


class SqlNotebook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.post = source.POST.read_text(encoding="utf-8")
        cls.notebook = json.loads(source.DESTINATION.read_text(encoding="utf-8"))
        cls.codes = [
            "".join(cell["source"])
            for cell in cls.notebook["cells"] if cell["cell_type"] == "code"
        ]
        cls.markdown = "\n".join(
            "".join(cell["source"])
            for cell in cls.notebook["cells"] if cell["cell_type"] == "markdown"
        )

    def test_exact_article_code_parity_and_generated_bytes(self):
        self.assertEqual(source.DESTINATION.read_bytes(), source.expected_bytes())
        expected = [
            match[2] for match in shared.FENCE.finditer(self.post)
            if match[1] == "sql"
        ]
        self.assertEqual(len(expected), 15)
        self.assertEqual(self.codes, expected)
        for code in self.codes:
            self.assertTrue(code.startswith("%%sql\n"))
            self.assertTrue(code.rstrip().endswith(";"))

    def test_source_metadata_is_for_sql_not_pipe(self):
        tutorial = self.notebook["metadata"]["tutorial"]
        self.assertEqual(tutorial, {
            "source": source.POST.relative_to(shared.ROOT).as_posix(),
            "source_sha256": hashlib.sha256(self.post.encode("utf-8")).hexdigest(),
        })
        pipe_post = shared.POST.read_text(encoding="utf-8")
        self.assertEqual(
            shared.build_notebook(pipe_post)["metadata"]["tutorial"]["source"],
            shared.POST.relative_to(shared.ROOT).as_posix(),
        )

    def test_format_kernel_and_clean_state(self):
        self.assertEqual((self.notebook["nbformat"], self.notebook["nbformat_minor"]), (4, 5))
        self.assertEqual(set(self.notebook["metadata"]), {
            "kernelspec", "language_info", "tutorial",
        })
        self.assertEqual(self.notebook["metadata"]["kernelspec"], {
            "display_name": "Synapse PySpark", "language": "python", "name": "synapse_pyspark",
        })
        ids = [cell["id"] for cell in self.notebook["cells"]]
        self.assertEqual(len(ids), len(set(ids)))
        for cell in self.notebook["cells"]:
            self.assertRegex(cell["id"], r"^[a-zA-Z0-9_-]{1,64}$")
            self.assertEqual(cell["metadata"], {})
            self.assertIsInstance(cell["source"], list)
            self.assertTrue(all(isinstance(line, str) for line in cell["source"]))
            if cell["cell_type"] == "code":
                self.assertIsNone(cell["execution_count"])
                self.assertEqual(cell["outputs"], [])
            else:
                self.assertEqual(cell["cell_type"], "markdown")
                self.assertNotIn("execution_count", cell)
                self.assertNotIn("outputs", cell)

    def test_title_first_and_portable_markdown(self):
        first = self.notebook["cells"][0]
        self.assertEqual(first["cell_type"], "markdown")
        self.assertEqual("".join(first["source"]).splitlines()[0],
                         "# Bring Your SQL Skills to Fabric Runtime 2.0")
        for unwanted in ("{{", "note-callout", 'class="note-title"', "<br><br>",
                         "## Adoption checklist", "# Before you run",
                         "## Your validation record",
                         "Note: This blog post was written with assistance from AI"):
            self.assertNotIn(unwanted, self.markdown)
        self.assertIn("Note: This blog post was written with assistance from AI", self.post)

    def test_download_instructions_are_blog_only_and_setup_is_preserved(self):
        relative = "/" + source.DESTINATION.relative_to(shared.ROOT).as_posix()
        self.assertIn(f"'{relative}' | relative_url", self.post)
        self.assertIn('download>Download the Spark SQL enhancements', self.post)
        self.assertIn("Import notebook", self.post)
        for omitted in (
            "## Download and import the companion notebook",
            "Choose either entry path",
            "- **Download:**",
            "- **Copy and paste:**",
            shared.SITE + relative,
        ):
            self.assertNotIn(omitted, self.markdown)
        for instruction in ("### Shared setup", "PySpark", "Runtime 2.0 Environment",
                            "Run all", "fresh Spark session"):
            self.assertIn(instruction, self.markdown)
        expected_markdown = "\n".join(
            "".join(cell["source"]) for cell in shared.article_cells(self.post)
            if cell["cell_type"] == "markdown"
        )
        start = expected_markdown.index("## Download and import the companion notebook\n")
        end = expected_markdown.index("### Shared setup\n", start)
        self.assertEqual(
            self.markdown, expected_markdown[:start] + expected_markdown[end:]
        )

    def test_script_boundaries_setup_and_expected_results(self):
        scripts = [code for code in self.codes if code.startswith("%%sql\nBEGIN\n")]
        self.assertEqual(len(scripts), 4)
        for script in scripts:
            self.assertTrue(script.rstrip().endswith("END;"))
        self.assertIn("CREATE OR REPLACE TEMP VIEW sql_sales", self.codes[1])
        self.assertIn("DECLARE OR REPLACE VARIABLE sql_min_sales", self.codes[3])
        self.assertIn("CREATE OR REPLACE TEMP VIEW sql_employees", self.codes[8])
        self.assertIn("WITH RECURSIVE", self.codes[9])
        self.assertIn("SQLSTATE 'P0001'", self.codes[13])
        self.assertIn("raise_error(", self.codes[13])
        self.assertIn("EXECUTE IMMEDIATE", self.codes[14])
        for result in ("| 6 | 6800.00 |", "| Chicago | 2400.00 |",
                       "| Frank | Carol | 2 |", "| Seattle | 1000.00 | 1500.00 |",
                       "REJECTED"):
            self.assertIn(result, self.markdown)

    def test_empty_batch_uses_row_count_not_revenue(self):
        script = self.codes[10]
        self.assertIn("DECLARE order_count BIGINT DEFAULT 0;", script)
        self.assertIn("SET VAR (order_count, total_sales)", script)
        self.assertIn("SELECT COUNT(*), COALESCE(SUM(amount), 0.00)", script)
        self.assertIn("IF order_count = 0 THEN", script)
        self.assertNotIn("IF total_sales = 0 THEN", script)
        self.assertIn(
            "SELECT order_count, total_sales, review_threshold, batch_status;", script
        )
        for expected in (
            "| 6 | 6800.00 | 6000.00 | REVIEW |",
            "| Empty batch | 0 | 0.00 | EMPTY |",
            "| Six zero-value orders | 6 | 0.00 | NORMAL |",
        ):
            self.assertIn(expected, self.markdown)

    def test_editorial_revision_and_requested_removals(self):
        for content in (self.post, self.markdown):
            self.assertIn("**Core path:**", content)
            self.assertIn("**Go further:**", content)
            self.assertIn("### Shared setup", content)
            self.assertIn("existing analytical SQL and SQL-based ETL workflows", content)
            self.assertNotIn(
                "Do not assume every statement in a script or every recursive "
                "operation runs natively.", content
            )
            self.assertNotIn("api/sql/index.html#raise_error", content)
            self.assertNotIn("sql-ref-syntax-aux-exec-imm.html", content)
            self.assertNotIn("## Start a self-contained Runtime 2.0 notebook", content)
            self.assertIn("a result**", content)

    def test_batch_aggregate_and_branch_expected_values(self):
        """Check portable SQL expressions in SQLite, not Spark script execution."""
        script = self.codes[10]
        aggregate = re.search(
            r"SET VAR \(order_count, total_sales\) = \(\s*(SELECT.*?)\s*\);",
            script, re.S,
        )
        branches = re.search(
            r"IF (.*?) THEN\s+SET VAR batch_status = ('[^']+');\s+"
            r"ELSEIF (.*?) THEN\s+SET VAR batch_status = ('[^']+');\s+"
            r"ELSE\s+SET VAR batch_status = ('[^']+');",
            script, re.S,
        )
        assert aggregate is not None, "Batch aggregate assignment missing"
        assert branches is not None, "Batch classification branches missing"
        amounts = [
            int(value) for value in re.findall(
                r"\(\d+,\s*'[^']+',\s*'[^']+',\s*(\d+)\)", self.codes[1]
            )
        ]
        self.assertEqual(len(amounts), 6)
        query = (
            f"WITH totals(order_count, total_sales) AS ({aggregate[1]}), "
            "parameters(review_threshold) AS (SELECT ?) "
            "SELECT order_count, total_sales, "
            f"CASE WHEN {branches[1]} THEN {branches[2]} "
            f"WHEN {branches[3]} THEN {branches[4]} ELSE {branches[5]} END "
            "FROM totals CROSS JOIN parameters"
        )
        connection = sqlite3.connect(":memory:")
        try:
            connection.execute("CREATE TABLE sql_sales(amount NUMERIC)")
            for values, threshold, expected in (
                (amounts, 6000, (6, 6800, "REVIEW")),
                (amounts, 7000, (6, 6800, "NORMAL")),
                ([], 6000, (0, 0, "EMPTY")),
                ([0] * 6, 6000, (6, 0, "NORMAL")),
                ([100, -100], 6000, (2, 0, "NORMAL")),
                ([6000], 6000, (1, 6000, "REVIEW")),
            ):
                with self.subTest(values=values, threshold=threshold):
                    connection.execute("DELETE FROM sql_sales")
                    connection.executemany(
                        "INSERT INTO sql_sales VALUES (?)", [(value,) for value in values]
                    )
                    self.assertEqual(
                        connection.execute(query, (threshold,)).fetchone(), expected
                    )
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
