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

## Author

**Arshad Ali** — Principal Product Manager at Microsoft, working on Microsoft Fabric Spark Runtime.
