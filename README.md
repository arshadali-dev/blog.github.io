# Arshad Ali — Blog

Source for [arshadali.dev](https://arshadali.dev), a blog sharing practical insights
on data and analytics engineering and product management.

## What to expect

- **Microsoft Fabric Spark Runtime** — feature deep dives, release explainers, and migration guidance
- **Performance and reliability** — practical tuning for real-world Spark workloads
- **Delta Lake, SQL, Python, and streaming** — production-relevant improvements
- **Data platform modernization** — patterns across Fabric and Azure Synapse
- **AI-ready data foundations** — agentic analytics and AI scenarios
- **Product management** — frameworks for product strategy, prioritization, and technical
  decision-making
- **System design for product managers** — practical examples and interview preparation

## Tech stack

- [Jekyll](https://jekyllrb.com/) static site generator
- [Type Theme](https://github.com/rohanchandra/type-theme) (customized)
- Cloudflare Pages for hosting, connected to GitHub `main`
- Dark/light mode toggle
- Categories, tags, search, and social share

## Homepage category views

The homepage offers Data Engineering and Product Management tabs. Data Engineering
is selected by default; `/?category=product-management` opens a shareable PM view.
Each category retains newest-first ordering and paginates independently with up to ten
posts per page (`&page=2` opens a second PM page when there are more than ten posts). Browser Back/Forward restores the
view, and keyboard users can switch tabs with arrow keys, Home, and End.
Posts appear directly below the tabs; category counts and page changes are announced
to screen readers without a repeated visible heading or summary.

Set `home_category_featured` to a post's category key to place it first in that
homepage category without changing its date or other chronological listings.
Product Sense is featured in Product Management. Unpublished posts appear only in
the unpublished preview, not production. With JavaScript disabled, both category
lists remain readable, with anchor links above them; older `/blog/pageN` links
normalize to the corresponding Data Engineering page when JavaScript is enabled.

## Post organization

Previous/next links at the bottom of each article follow publication order within
its categories, skipping unrelated posts. For articles with multiple categories,
sharing any category qualifies. A link is omitted when no matching post exists in
that direction; homepage featured ordering does not affect these links.

Store posts by publication year under `_posts/<year>/`, retaining the
`YYYY-MM-DD-slug.md` filename; for example,
`_posts/2026/2026-03-26-welcome.md`. Create a new year folder when needed.
Jekyll reads these subfolders without changing public URLs. Keep existing
`post_url` references unchanged; the dated filename still identifies the post.
When moving a source article, update its download generator's `POST` path and
regenerate companion notebooks to refresh their source-path metadata.

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

## Search discovery and AI visibility

Article URLs are extensionless, matching Cloudflare Pages' canonical routes.
Jekyll still writes the same `.html` files, so previously shared `.html` links
continue to redirect to the canonical URL. Do not add `.html` to new post
permalinks or hardcode article URLs; use `post.url` or Jekyll's `post_url` tag.
Local Jekyll preview also supports these extensionless paths.

Category keys, display names, and ordering are defined in
[`_data/categories.yml`](_data/categories.yml). Use each entry's `key` in post
front matter; for example, `Product-Management` displays as `Product Management`.
The category page also accepts the legacy display-name spelling and combines
both groups without duplicates. Category links use the display-name anchor;
the key anchor remains available when it differs. Do not rename post categories
just to change their display labels, because category keys affect article URLs.

The shared SEO image hook maps each post's `feature-img` to `image` for
`jekyll-seo-tag`, unless an explicit SEO image is provided. Author strings are
resolved through [`_data/authors.yml`](_data/authors.yml). Update both that
profile and the site-level author metadata if the author's profile URL changes.
Set `last_modified_at` only when an article has substantively changed; never
advance publication dates simply to imply freshness.

Browser/search titles are separate from editorial headlines. The homepage uses
`site.title` exactly; other pages default to `page.title | theme_settings.title`
with the shorter site branding. Set `seo_title` in front matter to override the
complete browser title, including any author suffix. This does not change the
visible headline, feed title, social headline, or structured-data headline.
The shared head renders one escaped `<title>` and disables only the SEO
plugin's title output, retaining its other metadata.

Each indexed page must have one nonempty H1. Site branding is an H1 only on
home/listing pages, where post cards use H2s. On article pages, use either a
`feature-title` heading or a Markdown H1, not both. A post without a feature
title still needs its own Markdown H1.

The [Fabric & Spark hub](fabric-spark.html) and [LLM index](llms.txt) are
generated from published posts during each build. The LLM index is a convenience
for tools that choose to consume it, not a Google ranking factor or a guarantee
of AI citation or model training. The custom [404 page](404.html) prevents
Cloudflare's default homepage fallback from turning missing URLs into soft 404s.

CI and live verification check canonical URLs, sitemap/feed/search agreement,
single-title/single-H1 structure, editorial headline agreement, article
descriptions, author attribution, banner metadata, the generated LLM
index, and the topic hub. Live verification also checks the latest article's legacy redirect
and a genuinely missing URL's HTTP 404 response.

The existing Google Analytics integration records `file_download` clicks for
same-site `.ipynb` and `.py` links under `assets/downloads/`, without URL query
strings. Standard formats such as ZIP are left to GA4 Enhanced Measurement to
avoid duplicate events. Enable file-download Enhanced Measurement in the GA4
property for those formats. These are click events, not proof of completed
downloads or notebook execution.

After successful verification of the current production revision, the deployment
workflow submits the sitemap's public HTML URLs to IndexNow. This small site
submits its complete current URL set once per deployment, not just changed posts;
there is no scheduled resubmission. Preview builds and PR checks never submit.
[`indexnow-key.txt`](indexnow-key.txt) is a deliberately public ownership proof,
not an account credential. No Google, Bing, or Cloudflare credentials belong in
the repository. The script confirms the deployed revision and public proof file
before submitting; HTTP errors fail the workflow rather than claiming success.
HTTP 200 means received; HTTP 202 means accepted pending key validation. Neither
means indexed. An IndexNow failure does not roll back an already live deployment.

After correcting a submission failure, rerun **Verify production deployment**
for the current `main` revision. To notify engines about a removed URL, first
deploy its removal or redirect, then run:

```shell
python .github/scripts/submit_indexnow.py --url https://arshadali.dev --revision <commit-sha> --deleted-url https://arshadali.dev/old-article
```

### Owner setup and ongoing monitoring

These account steps cannot be replaced by repository configuration:

1. In [Google Search Console](https://search.google.com/search-console), add or
   select the `arshadali.dev` Domain property and verify it using Google's DNS TXT
   record in Cloudflare. Submit `https://arshadali.dev/sitemap.xml`, inspect the
   canonical article URL, run the live URL test, and request indexing. If a
   property is already verified, reuse it rather than creating a duplicate.
2. In [Bing Webmaster Tools](https://www.bing.com/webmasters), verify the site
   (or import an existing verified Search Console property), submit the same
   sitemap, and inspect indexing and IndexNow submission reports.
3. In Cloudflare, review WAF events and AI Crawl Control. Allow the desired
   verified search crawlers, including Googlebot, Bingbot, and OAI-SearchBot,
   without disabling general security protections. Use provider verification or
   published IP ranges, not a user-agent-only bypass. Search permission and
   training permission are independent; this change does not alter either
   robots rules or AI-training settings.
4. Monitor Search Console impressions, clicks, indexed/excluded pages; Bing
   indexing and AI Performance citations; and Analytics referral traffic.
   Search referrals and AI citations are different metrics. Crawling, indexing,
   ranking, citation, and model training are not guaranteed by any of these steps.

### Monthly discovery review

Once a month, compare the last 28 complete days with the preceding 28 days.
Keep account exports and measurements privately, outside the public repository.
Record the reporting dates, affected URLs, observations, and one next action.

| Check | Source | Follow-up |
| --- | --- | --- |
| Article indexing and selected canonical | Google Search Console URL Inspection and Page indexing; Bing URL Inspection | Inspect canonical article URLs. Distinguish unexpected exclusions from expected legacy redirects and duplicate URLs. |
| Search reach | Search Console and Bing performance reports | Compare impressions, clicks, queries, and landing pages. Improve weak titles or coverage based on actual queries, not keyword stuffing. |
| AI citations | Bing AI Performance | Track cited pages and citation trends within its supported experiences. Citations are not visits, rankings, or coverage of every AI service. |
| Reader engagement | GA4 acquisition and events | Check referrals and notebook-download clicks; confirm the intended property receives data before interpreting missing events as zero activity. |
| Crawl failures | Search Console crawl reports and Cloudflare security/bot reports | Investigate persistent errors or challenges affecting verified crawlers without weakening security controls. |

Use the sitemap for discovery across the site. Request indexing for a newly
published or materially updated priority article after a successful live test;
do not repeatedly submit unchanged URLs. Account reports can lag deployments.
Keep a record of changes so the next review can compare outcomes without
assuming that a correlation proves an SEO or AI-citation effect.

### Authoring and distribution

For new posts, provide a clear answer, supported runtime/version, runnable
examples, limitations, and evidence in the HTML itself. Share a useful summary
with a link through relevant communities or newsletters; avoid bulk link spam.

- Add descriptive contextual links to genuinely related articles. Expand a
  topic hub when there is a useful collection, rather than creating thin pages.
- Link the blog from profiles and author pages you control. Publish original
  summaries on relevant channels; obtain approval before posting on someone's
  behalf. If republishing full text, use an original-source canonical where the
  platform supports it; otherwise prefer an excerpt and link.
- Use concise browser titles without changing editorial headlines. Roughly
  50-60 characters is a useful review target, not a hard indexing limit.
- Preserve dated historical context and original evidence. Do not invent
  benchmark results, inflate update dates, or add special AI markup in place of
  useful content. Search-crawler access and model-training permission are
  separate decisions.

References: [Google AI search guidance](https://developers.google.com/search/docs/appearance/ai-features),
[OpenAI crawler controls](https://developers.openai.com/api/docs/bots),
[IndexNow protocol](https://www.indexnow.org/documentation).

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

The [pipe syntax tutorial](_posts/2026/2026-10-19-pipe-syntax-spark-4-1-fabric-runtime-2-0.md)
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

The [SQL enhancements tutorial](_posts/2026/2026-11-17-spark-sql-enhancements-fabric-runtime-2-0.md)
is the source of truth for its
[downloadable notebook](assets/downloads/fabric-sql-enhancements/spark-sql-runtime-2-0.ipynb).
The generator reuses the pipe tutorial's Markdown/cell conversion, preserves
all PySpark blocks verbatim and in order, and records this article's path and
SHA-256. Both notebooks start with their article title, omit the blog-only
AI disclosure, and contain no outputs or workspace bindings.
The SQL notebook also omits the blog's download/import introduction while
retaining the shared setup instructions and every executable example.
Each cell executes SQL statements or a complete script with `spark.sql(...)`.
The dynamic SQL cell initializes two session variables before executing its script.
Result-producing cells use `.show(truncate=False)`; setup and assignments do not.

After editing the article, use Python 3.11+ (standard library only):

```shell
python .github/scripts/sync_sql_notebook.py
python .github/scripts/sync_sql_notebook.py --check
python -m unittest discover -s .github/scripts -p "test_*notebook.py"
```

These tests check the notebook contract, session-parameter initialization order, and
portable filter/aggregate expressions in SQLite, including quoted city names and
unmatched values. They do not execute Spark SQL scripting or validate Spark variable scope.
Import the
notebook into Fabric, select a published Runtime 2.0 Environment, and run all
15 PySpark cells in a fresh session. Compare the expected tables, including
the deliberate `REJECTED` result from the handler example. Try the two suggested
threshold edits and empty/zero-value batch exercises separately, restore the
original values and queries, then repeat in a
fresh session. Retain the executed copy and environment record privately.
Do not manually edit the generated public download.

## Author

**Arshad Ali** — Principal Product Manager at Microsoft, working on Microsoft Fabric Spark Runtime.
