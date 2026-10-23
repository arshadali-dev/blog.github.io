"""Generate the reader notebook from the pipe-syntax post without running Spark."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
from typing import NotRequired, TypedDict

ROOT = Path(__file__).resolve().parents[2]
POST = ROOT / "_posts" / "2026-10-19-pipe-syntax-spark-4-1-fabric-runtime-2-0.md"
DESTINATION = (
    ROOT / "assets" / "downloads" / "fabric-pipe-syntax"
    / "pipe-syntax-runtime-2-0.ipynb"
)
SITE = "https://arshadali.dev"
FENCE = re.compile(r"^```([^\n]*)\n(.*?)^```[ \t]*(?:\n|\Z)", re.M | re.S)


class Cell(TypedDict):
    cell_type: str
    id: str
    metadata: dict[str, object]
    source: list[str]
    execution_count: NotRequired[None]
    outputs: NotRequired[list[object]]


class Notebook(TypedDict):
    cells: list[Cell]
    metadata: dict[str, object]
    nbformat: int
    nbformat_minor: int


def notebook_markdown(text: str) -> str:
    text = re.sub(
        r"^> \*Note: This blog post was written with assistance from AI\*[ \t]*$",
        "",
        text,
        flags=re.M,
    )
    text = re.sub(
        r"\{\{\s*'([^']+)'\s*\|\s*relative_url\s*\}\}",
        lambda match: SITE + match[1],
        text,
    )
    text = re.sub(
        r'<a href="([^"]+)" download>(.*?)</a>',
        r"[\2](\1)",
        text,
    )
    text = text.replace('<div class="note-callout" markdown="1">', "")
    text = re.sub(r'<div class="note-title">(.*?)</div>', r"**\1**", text)
    text = text.replace("</div>", "").replace("<br><br>", "\n\n")
    return text.strip()


def article_cells(post: str) -> list[Cell]:
    front_matter = re.match(r"\A---\n.*?\n---\n", post, re.S)
    if front_matter is None:
        raise ValueError("Post must start with YAML front matter.")
    body = post[front_matter.end():]
    matches = list(FENCE.finditer(body))
    if len(re.findall(r"^```", body, re.M)) != 2 * len(matches):
        raise ValueError("Post contains an unclosed or unsupported code fence.")

    cells: list[Cell] = []

    def append(kind: str, content: str) -> None:
        if kind == "markdown":
            content = notebook_markdown(content)
        if not content.strip():
            return
        cell: Cell = {
            "cell_type": kind,
            "id": f"article-{len(cells):03d}",
            "metadata": {},
            "source": content.splitlines(keepends=True),
        }
        if kind == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
        cells.append(cell)

    cursor = 0
    for match in matches:
        append("markdown", body[cursor:match.start()])
        language, code = match[1].strip(), match[2]
        if language == "python":
            ast.parse(code)
            append("code", code)
        elif language == "sql":
            if not code.startswith("%%sql\n") or not code.rstrip().endswith(";"):
                raise ValueError("SQL cells must start with %%sql and end with a semicolon.")
            append("code", code)
        elif language == "text":
            append("markdown", match[0])
        else:
            raise ValueError(f"Unsupported fenced-block language: {language!r}")
        cursor = match.end()
    append("markdown", body[cursor:])
    if not any(cell["cell_type"] == "code" for cell in cells):
        raise ValueError("Post contains no executable examples.")
    return cells


def build_notebook(post: str) -> Notebook:
    digest = hashlib.sha256(post.encode("utf-8")).hexdigest()
    return {
        "cells": article_cells(post),
        "metadata": {
            "kernelspec": {
                "display_name": "Synapse PySpark",
                "language": "python",
                "name": "synapse_pyspark",
            },
            "language_info": {"name": "python"},
            "tutorial": {
                "source": POST.relative_to(ROOT).as_posix(),
                "source_sha256": digest,
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def expected_bytes() -> bytes:
    post = POST.read_text(encoding="utf-8")
    notebook = build_notebook(post)
    return (json.dumps(notebook, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the download is stale.")
    args = parser.parse_args()
    content = expected_bytes()
    if args.check:
        if not DESTINATION.is_file() or DESTINATION.read_bytes() != content:
            raise SystemExit("Notebook is missing or stale. Run sync_pipe_notebook.py.")
        print("Notebook matches the article; no Spark execution performed.")
        return
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_bytes(content)
    print(f"Generated {DESTINATION.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
