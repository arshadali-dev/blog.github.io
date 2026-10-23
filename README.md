# Arshad Ali — Blog

Source for [arshadali.dev](https://arshadali.dev), a technical blog covering Microsoft Fabric, Spark Runtime, and data platform modernization.

## What to expect

- **Microsoft Fabric Spark Runtime** — feature deep dives, release explainers, and migration guidance
- **Performance and reliability** — practical tuning for real-world Spark workloads
- **Delta Lake, SQL, Python, and streaming** — production-relevant improvements
- **Data platform modernization** — patterns across Fabric and Azure Synapse
- **AI-ready data foundations** — agentic analytics and AI scenarios

## Tech stack

- [Jekyll](https://jekyllrb.com/) static site generator
- [Type Theme](https://github.com/rohanchandra/type-theme) (customized)
- GitHub Pages for hosting
- Dark/light mode toggle
- Categories, tags, search, and social share

## Local preview

Install Ruby 3.4 (with Devkit on Windows), then run from the repository root:

```shell
bundle install
bundle exec jekyll serve --host 127.0.0.1 --port 4000
```

Open <http://127.0.0.1:4000/>. Jekyll builds the site before serving it and
rebuilds when posts, layouts, or assets change. Refresh the browser after a
rebuild; restart Jekyll after changing `_config.yml`.

Alternatively, run **Tasks: Run Task > Preview site** in VS Code. The Windows
task adds `%LOCALAPPDATA%\Programs\Ruby34-x64\bin` to its PATH for a per-user
Ruby installation; Ruby installed elsewhere must be available on your PATH.
Stop the preview with **Ctrl+C** in its terminal.

Do not use a static HTTP server against `_site` to preview source edits:
it only serves the last generated build and cannot pick up new posts.

## Livy example downloads

The Livy post's standalone downloads are generated from its Python blocks.
The two advanced example bodies are maintained in
`.github/scripts/sync_livy_examples.py`. After changing an example, regenerate
the downloads and check that the article, scripts, and ZIP agree:

```shell
python .github/scripts/sync_livy_examples.py
python .github/scripts/sync_livy_examples.py --check
python -m unittest discover -s .github/scripts -p test_livy_examples.py
```

Use Python 3.11+ with the client dependencies from
`assets/downloads/fabric-livy/requirements.txt`. The tests mock Fabric calls;
they do not submit workloads. Update the post's tested-on record only after
live validation of the actual downloads, including output and cleanup checks.

## Pipe syntax companion notebook

The [pipe syntax tutorial](_posts/2026-10-19-pipe-syntax-spark-4-1-fabric-runtime-2-0.md)
is the source of truth for its
[downloadable notebook](assets/downloads/fabric-pipe-syntax/pipe-syntax-runtime-2-0.ipynb).
The generator preserves every Python and SQL block in order, keeps SQL magics,
converts article callouts to portable Markdown, and records a source SHA-256.
Do not manually edit the generated notebook.

After editing the article, use Python 3.11+ (standard library only):

```shell
python .github/scripts/sync_pipe_notebook.py
python .github/scripts/sync_pipe_notebook.py --check
python -m unittest discover -s .github/scripts -p test_pipe_notebook.py
```

These are offline checks, not Spark execution. For live validation, import the
download into Fabric, select a published Runtime 2.0 Environment, use PySpark as
the default language, and run all cells in a fresh session without a Lakehouse.
Check expected tables and assertions, then repeat after restarting.
Retain the executed copy privately with your environment details and outputs;
keep the public download output-free and unbound to any workspace. Only update
the article and generator's validation status after a successful live run.

## Author

**Arshad Ali** — Principal Product Manager at Microsoft, working on Microsoft Fabric Spark Runtime.
