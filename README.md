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
- Cloudflare Pages for hosting, connected to GitHub `main`
- Dark/light mode toggle
- Categories, tags, search, and social share

## Local preview

Production and Linux CI use the Ruby version in [`.ruby-version`](.ruby-version).
For local development, install Ruby 3.4 (with Devkit on Windows), then run from
the repository root:

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

## Build and deployment safeguards

The shared [build script](.github/scripts/build_site.rb) invokes Jekyll through
Bundler with strict front-matter validation. It writes `build-info.json` into
the generated site only after a successful build, recording the source commit
for deployment verification. Do not invoke bare `jekyll build`: globally
installed gems can conflict with the versions in `Gemfile.lock`.

Use this exact build command locally, in CI, and in Cloudflare:

```shell
ruby .github/scripts/build_site.rb
```

Cloudflare Pages project: `arshadali-dev-blog`

| Setting | Value |
|---|---|
| Production branch | `main` |
| Root directory | Repository root |
| Build command | `ruby .github/scripts/build_site.rb` |
| Build output directory | `_site` |
| Ruby version | Read from `.ruby-version` |
| Bundler and gem versions | Read from `Gemfile.lock` |

Keep both Windows and Linux platforms in the lockfile. After an intentional
dependency update, use `bundle lock --add-platform x86_64-linux`, review the
lockfile changes, and validate both the local build and Linux CI. Do not remove
or regenerate the lockfile merely to bypass an installation failure.

The [Blog CI workflow](.github/workflows/ci.yml) runs on pull requests and pushes
to `main`. It installs locked Ruby dependencies and the existing pinned Livy
client requirements on Ubuntu, runs offline regression tests and
generated-download checks, builds the site, and checks its content.
Repository-owner setup (requires GitHub admin access): protect `main`, require
a pull request, and require **Build and test (Ubuntu)** with the branch up to
date before merging. Zero additional approvals can be required for solo work.
Adding a workflow alone does not enforce these branch-protection settings.

The [production verification workflow](.github/workflows/verify-deployment.yml)
runs after the Cloudflare Pages check completes for `main`. A failed Cloudflare
deployment fails the workflow. A successful deployment must serve the expected
commit, the latest article on the homepage, its feed/search/sitemap entries,
and correctly typed local images, stylesheets, and scripts. HTTP 200 alone is
insufficient because Cloudflare can return the homepage for a missing resource.
Superseded commits are skipped; verification retries briefly for propagation.

Run the same checks manually with a full commit SHA:

```shell
python .github/scripts/verify_site.py --directory _site --revision <commit-sha>
python .github/scripts/verify_site.py --url https://arshadali.dev --revision <commit-sha> --attempts 6
```

### If a deployment fails

1. Open the **Cloudflare Pages** check for the commit and inspect the first
   actual error in its build log. A successful Git push is not publication.
2. Verify the dashboard build command is exactly the one above, without diff
   markers, Markdown fences, or an old command appended to it.
3. Retry once for a transient download or service failure. For reproducible
   failures, fix the source or configuration through a tested pull request.
4. Confirm both the Cloudflare deployment and **Verify live site** checks pass
   before announcing publication.

Use the project's Cloudflare Pages failure notification policy for build or
deployment failures. GitHub Actions notifications cover CI and live-content
verification failures; enable failed-workflow email notifications in personal
GitHub notification settings. The last successful production deployment remains
available when a new build fails.

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

ZIP timestamps and creator-platform metadata are fixed so Windows and Linux
produce the same download.

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

## SQL enhancements companion notebook

The [SQL enhancements tutorial](_posts/2026-10-23-spark-sql-enhancements-fabric-runtime-2-0.md)
is the source of truth for its
[downloadable notebook](assets/downloads/fabric-sql-enhancements/spark-sql-runtime-2-0.ipynb).
The generator reuses the pipe tutorial's Markdown/cell conversion, preserves
all SQL blocks verbatim and in order, and records this article's path and
SHA-256. Both notebooks start with their article title, omit the blog-only
AI disclosure, and contain no outputs or workspace bindings.
The SQL notebook also omits the blog's download/import introduction while
retaining the shared setup instructions and every executable example.

After editing the article, use Python 3.11+ (standard library only):

```shell
python .github/scripts/sync_sql_notebook.py
python .github/scripts/sync_sql_notebook.py --check
python -m unittest discover -s .github/scripts -p "test_*notebook.py"
```

These tests check the notebook contract and evaluate the batch example's
portable aggregate/branch expressions in SQLite, not Spark SQL scripting.
Import the
notebook into Fabric, select a published Runtime 2.0 Environment, and run all
15 SQL cells in a fresh PySpark session. Compare the expected tables, including
the deliberate `REJECTED` result from the handler example. Try the two suggested
threshold edits and empty/zero-value batch exercises separately, restore the
original values and queries, then repeat in a
fresh session. Retain the executed copy and environment record privately.
Do not manually edit the generated public download.

## Author

**Arshad Ali** — Principal Product Manager at Microsoft, working on Microsoft Fabric Spark Runtime.
