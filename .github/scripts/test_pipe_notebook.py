"""Offline notebook tests. These do not run Spark or contact Fabric."""

import ast
from collections import defaultdict
from decimal import Decimal
import hashlib
import json
import re
import unittest

import sync_pipe_notebook as source


class PipeNotebook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.post = source.POST.read_text(encoding="utf-8")
        cls.notebook = json.loads(source.DESTINATION.read_text(encoding="utf-8"))
        cls.codes = [
            "".join(cell["source"])
            for cell in cls.notebook["cells"]
            if cell["cell_type"] == "code"
        ]

    def test_download_matches_article(self):
        self.assertEqual(source.DESTINATION.read_bytes(), source.expected_bytes())
        expected = [
            match[2] for match in source.FENCE.finditer(self.post)
            if match[1] in ("python", "sql")
        ]
        self.assertEqual(self.codes, expected)

    def test_notebook_structure_and_no_execution_state(self):
        self.assertEqual((self.notebook["nbformat"], self.notebook["nbformat_minor"]), (4, 5))
        ids = [cell["id"] for cell in self.notebook["cells"]]
        self.assertEqual(len(ids), len(set(ids)))
        for cell in self.notebook["cells"]:
            with self.subTest(cell=cell["id"]):
                self.assertRegex(cell["id"], r"^[a-zA-Z0-9_-]{1,64}$")
                self.assertIsInstance(cell["source"], list)
                self.assertTrue(all(isinstance(line, str) for line in cell["source"]))
                self.assertEqual(cell["metadata"], {})
                if cell["cell_type"] == "code":
                    self.assertIsNone(cell["execution_count"])
                    self.assertEqual(cell["outputs"], [])
                else:
                    self.assertEqual(cell["cell_type"], "markdown")
                    self.assertNotIn("outputs", cell)
        self.assertEqual(
            set(self.notebook["metadata"]), {"kernelspec", "language_info", "tutorial"}
        )
        self.assertEqual(self.notebook["metadata"]["kernelspec"]["language"], "python")
        self.assertEqual(self.notebook["metadata"]["kernelspec"]["name"], "synapse_pyspark")

    def test_revision_metadata(self):
        tutorial = self.notebook["metadata"]["tutorial"]
        digest = hashlib.sha256(self.post.encode("utf-8")).hexdigest()
        self.assertEqual(tutorial["source_sha256"], digest)
        self.assertNotIn("live_fabric_validation", tutorial)

    def test_title_first_and_removed_sections_stay_absent(self):
        first = self.notebook["cells"][0]
        self.assertEqual(first["cell_type"], "markdown")
        self.assertEqual(
            "".join(first["source"]).splitlines()[0],
            "# Spark SQL That Reads Like PySpark",
        )
        content = "\n".join("".join(cell["source"]) for cell in self.notebook["cells"])
        for heading in (
            "## Adoption checklist",
            "### Optional cleanup",
            "# Before you run",
            "## Your validation record",
        ):
            with self.subTest(heading=heading):
                self.assertNotIn(heading, content)
                self.assertNotIn(heading, self.post)
        self.assertNotIn("dropTempView", content)
        self.assertNotIn("cleanup", content.lower())

    def test_python_syntax_and_sql_cell_format(self):
        for index, code in enumerate(self.codes):
            with self.subTest(index=index):
                if code.startswith("%%sql\n"):
                    self.assertTrue(code.rstrip().endswith(";"))
                else:
                    ast.parse(code)
                    self.assertNotIn("%%sql", code)

    def test_markdown_is_portable_and_retains_expected_results(self):
        markdown = "\n".join(
            "".join(cell["source"]) for cell in self.notebook["cells"]
            if cell["cell_type"] == "markdown"
        )
        for unwanted in ("{{", "note-callout", 'class="note-title"', "<br><br>"):
            self.assertNotIn(unwanted, markdown)
        self.assertIn("```text\nSales ->", markdown)
        self.assertIn("| 1 | East | 4 | 5200.00 |", markdown)
        self.assertIn("https://arshadali.dev/assets/downloads/", markdown)

    def test_notebook_omits_blog_disclosure_and_preserves_setup_wording(self):
        markdown = "\n".join(
            "".join(cell["source"]) for cell in self.notebook["cells"]
            if cell["cell_type"] == "markdown"
        )
        disclosure = "Note: This blog post was written with assistance from AI"
        self.assertIn(disclosure, self.post)
        self.assertNotIn(disclosure, markdown)
        paragraph = next(
            line for line in self.post.splitlines()
            if line.startswith("The examples below use session-scoped temporary views.")
        )
        self.assertIn("For the purpose of the examples in this blog,", paragraph)
        self.assertIn(paragraph, markdown)

    def test_clean_run_dependencies_and_plan_ordering(self):
        init = next(i for i, code in enumerate(self.codes) if "sales = spark.table" in code)
        sales_view = next(i for i, code in enumerate(self.codes) if "TEMP VIEW pipe_sales AS" in code)
        city_view = next(i for i, code in enumerate(self.codes) if "TEMP VIEW pipe_city_info AS" in code)
        self.assertGreater(init, max(sales_view, city_view))
        self.assertIn("from pyspark.sql.window import Window", self.codes[init])
        regional_view = [code for code in self.codes if "TEMP VIEW pipe_top_regions AS" in code]
        self.assertEqual(len(regional_view), 1)
        for variable in ("pyspark_result", "pipe_result"):
            code = next(code for code in self.codes if f"{variable} =" in code)
            self.assertIn('.orderBy("revenue_rank")', code)

    def test_new_filter_and_sample_result_arithmetic(self):
        setup = next(code for code in self.codes if "TEMP VIEW pipe_sales AS" in code)
        pattern = r"\((\d+),\s*'([^']+)',\s*'([^']+)',\s*'([^']+)',\s*(\d+),\s*(\d+)\)"
        rows = [
            (int(i), city, category, Decimal(price), int(qty))
            for i, city, product, category, price, qty in re.findall(pattern, setup)
        ]
        self.assertEqual(len(rows), 8)
        cities = defaultdict(Decimal)
        electronics = defaultdict(Decimal)
        units = defaultdict(int)
        for _, city, category, price, qty in rows:
            cities[city] += price * qty
            if category == "Electronics":
                electronics[city] += price * qty
                units[city] += qty
        self.assertEqual(sum(cities.values()), Decimal("17100"))
        filtered = sorted(
            ((city, total) for city, total in cities.items() if total > 4000),
            key=lambda row: (-row[1], row[0]),
        )
        self.assertEqual(filtered, [("New York", Decimal(6200)), ("Austin", Decimal(4550))])
        section = self.post.split("## 5. ")[1].split("### Position gives WHERE")[0]
        self.assertIn("HAVING SUM(price * quantity) > 4000", section)
        self.assertIn("|> WHERE total_revenue > 4000", section)
        self.assertIn('.filter(F.col("total_revenue") > 4000)', section)
        lookup = next(code for code in self.codes if "TEMP VIEW pipe_city_info AS" in code)
        regions = dict(re.findall(r"\('([^']+)',\s*'([^']+)'\)", lookup))
        expected = [
            (rank, regions[city], units[city], total)
            for rank, (city, total) in enumerate(
                sorted(electronics.items(), key=lambda row: (-row[1], regions[row[0]]))[:3], 1
            )
        ]
        self.assertEqual(expected, [
            (1, "East", 4, Decimal(5200)),
            (2, "West", 5, Decimal(3600)),
            (3, "South", 4, Decimal(1800)),
        ])
        for rank, region, count, total in expected:
            self.assertIn(f"| {rank} | {region} | {count} | {total:.2f} |", self.post)

    def test_generation_rejects_invalid_fences_and_python(self):
        for body in ("```sql\nSELECT 1;\n```", "```bash\necho bad\n```", "```python\nx = 1"):
            with self.subTest(body=body), self.assertRaises(ValueError):
                source.article_cells("---\ntitle: Test\n---\n" + body)
        with self.assertRaises(SyntaxError):
            source.article_cells("---\ntitle: Test\n---\n```python\nif\n```\n")


if __name__ == "__main__":
    unittest.main()
