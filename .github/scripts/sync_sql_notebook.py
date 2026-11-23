"""Generate the SQL enhancements notebook from its article without running Spark."""

import argparse
import json
import re

from sync_pipe_notebook import ROOT, build_notebook

POST = ROOT / "_posts" / "2026" / "2026-11-17-spark-sql-enhancements-fabric-runtime-2-0.md"
DESTINATION = (
    ROOT / "assets" / "downloads" / "fabric-sql-enhancements"
    / "spark-sql-runtime-2-0.ipynb"
)


def expected_bytes() -> bytes:
    post = POST.read_text(encoding="utf-8")
    notebook = build_notebook(post, source_path=POST)
    removed = 0
    for cell in notebook["cells"]:
        if cell["cell_type"] != "markdown":
            continue
        markdown, count = re.subn(
            r"^## Download and import the companion notebook\n.*?"
            r"(?=^### Shared setup$)",
            "",
            "".join(cell["source"]),
            flags=re.M | re.S,
        )
        cell["source"] = markdown.splitlines(keepends=True)
        removed += count
    if removed != 1:
        raise ValueError(
            "Expected one download/import section followed by Shared setup; "
            "check the article headings before regenerating."
        )
    return (json.dumps(notebook, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the download is stale.")
    args = parser.parse_args()
    content = expected_bytes()
    if args.check:
        if not DESTINATION.is_file() or DESTINATION.read_bytes() != content:
            raise SystemExit("Notebook is missing or stale. Run sync_sql_notebook.py.")
        print("Notebook matches the article; no Spark execution performed.")
        return
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_bytes(content)
    print(f"Generated {DESTINATION.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
