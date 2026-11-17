"""Regression tests for deployment checks, including Cloudflare's HTTP-200 fallback."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from verify_site import (
    Page, directory_reader, http_reader, local_path, sitemap_urls, verify, verify_live_routes,
)

REVISION = "a" * 40
ARTICLE = "/product%20management/2026/11/14/guide"
ORIGIN = "https://example.test/"


class VerifySite(unittest.TestCase):
    def setUp(self):
        article_url = ORIGIN.rstrip("/") + ARTICLE
        image_url = ORIGIN + "assets/diagram.svg"
        schema = {
            "@context": "https://schema.org", "@type": "BlogPosting", "url": article_url,
            "headline": "A & B",
            "author": {"name": "Author", "url": ORIGIN + "about/"},
            "datePublished": "2026-11-14", "dateModified": "2026-11-14", "image": image_url,
        }
        self.files = {
            "/build-info.json": (
                json.dumps({"revision": REVISION}).encode(), "application/json",
            ),
            "/": (
                (f'<title>Blog</title><link rel="canonical" href="{ORIGIN}">'
                 '<meta name="description" content="Blog description">'
                 f'<h1>Blog</h1><a href="{ARTICLE}">Guide</a>').encode(), "text/html",
            ),
            "/feed.xml": (
                f"<rss><channel><title>Blog</title><link>{ORIGIN}</link><item><title>A &amp; B</title>"
                f"<link>{ORIGIN.rstrip('/')}{ARTICLE}</link></item></channel></rss>".encode(),
                "application/xml",
            ),
            ARTICLE: (
                (f'<title>A &amp; B | Blog</title>'
                 f'<link rel="canonical" href="{article_url}">'
                 '<meta name="description" content="A practical guide">'
                 '<meta property="og:type" content="article">'
                 '<meta property="og:title" content="A &amp; B">'
                 f'<meta property="og:url" content="{article_url}">'
                 f'<meta property="og:image" content="{image_url}">'
                 f'<meta name="twitter:image" content="{image_url}">'
                 f'<script type="application/ld+json">{json.dumps(schema)}</script>'
                 '<h1>A &amp; B</h1>'
                 '<nav aria-label="Related guides"><a href="/fabric-spark/">More</a></nav>'
                 '<img class="feature-img" src="/assets/diagram.svg">'
                 '<link rel="stylesheet" href="/assets/site.css">'
                 '<script src="/assets/site.js"></script>'
                 '<img src="https://external.test/image.png">').encode(),
                "text/html",
            ),
            "/sitemap.xml": (
                f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                f"<url><loc>{ORIGIN}</loc></url>"
                f"<url><loc>{ORIGIN.rstrip('/')}{ARTICLE}</loc></url></urlset>".encode(),
                "application/xml",
            ),
            "/search/": (ARTICLE.encode(), "text/html"),
            "/assets/diagram.svg": (b"<svg/>", "image/svg+xml"),
            "/assets/site.css": (b"body {}", "text/css"),
            "/assets/site.js": (b"console.log('ok')", "text/javascript"),
            "/llms.txt": (f"- [A & B]({article_url}): A practical guide\n".encode(), "text/plain"),
            "/robots.txt": (b"User-agent: *\nAllow: /\n", "text/plain"),
            "/fabric-spark/": (f'<a href="{ARTICLE}">A &amp; B</a>'.encode(), "text/html"),
            "/404": (b'<meta name="robots" content="noindex, follow">Not found', "text/html"),
        }

    def read(self, path):
        if path not in self.files:
            raise FileNotFoundError(path)
        return self.files[path]

    def test_valid_site_and_external_assets_are_not_fetched(self):
        self.assertEqual(verify(self.read, REVISION), (ARTICLE, 3))

    def test_stale_deployment_fails(self):
        with self.assertRaisesRegex(ValueError, "expected revision"):
            verify(self.read, "b" * 40)

    def test_metadata_fallback_fails(self):
        self.files["/build-info.json"] = self.files["/"]
        with self.assertRaisesRegex(ValueError, "fallback"):
            verify(self.read, REVISION)

    def test_article_fallback_with_status_200_fails(self):
        self.files[ARTICLE] = self.files["/"]
        with self.assertRaisesRegex(ValueError, "fallback"):
            verify(self.read, REVISION)

    def test_asset_fallback_with_status_200_fails(self):
        self.files["/assets/diagram.svg"] = self.files["/"]
        with self.assertRaisesRegex(ValueError, "wrong type"):
            verify(self.read, REVISION)

    def test_missing_asset_fails(self):
        del self.files["/assets/diagram.svg"]
        with self.assertRaises(FileNotFoundError):
            verify(self.read, REVISION)

    def test_missing_homepage_link_fails(self):
        self.files["/"] = (b"<title>Blog</title>", "text/html")
        with self.assertRaisesRegex(ValueError, "homepage"):
            verify(self.read, REVISION)

    def test_missing_sitemap_entry_fails(self):
        self.files["/sitemap.xml"] = (b"<urlset/>", "application/xml")
        with self.assertRaisesRegex(ValueError, "sitemap"):
            verify(self.read, REVISION)

    def test_missing_search_entry_fails(self):
        self.files["/search/"] = (b"{}", "text/html")
        with self.assertRaisesRegex(ValueError, "search"):
            verify(self.read, REVISION)

    def test_empty_feed_fails(self):
        self.files["/feed.xml"] = (
            f"<rss><channel><title>Blog</title><link>{ORIGIN}</link></channel></rss>".encode(),
            "application/xml",
        )
        with self.assertRaisesRegex(ValueError, "latest article"):
            verify(self.read, REVISION)

    def test_url_normalization(self):
        self.assertEqual(local_path("/product management/a.html", ORIGIN),
                         "/product%20management/a.html")
        self.assertEqual(local_path("../diagram.svg", ORIGIN + "posts/guide.html"),
                         "/diagram.svg")
        self.assertIsNone(local_path("//external.test/image.png", ORIGIN))

    def test_directory_reader_handles_encoded_paths_and_blocks_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "product management").mkdir()
            (root / "product management" / "index.html").write_text("ok", encoding="utf-8")
            (root / "article.html").write_text("article", encoding="utf-8")
            read = directory_reader(root)
            self.assertEqual(read("/product%20management/"), (b"ok", "text/html"))
            self.assertEqual(read("/article"), (b"article", "text/html"))
            with self.assertRaisesRegex(ValueError, "escapes"):
                read("/%2e%2e/outside.html")

    def replace_article(self, old, new):
        content, kind = self.files[ARTICLE]
        self.files[ARTICLE] = (content.replace(old.encode(), new.encode()), kind)

    def test_independent_seo_title_preserves_editorial_identity(self):
        self.replace_article("<title>A &amp; B | Blog</title>",
                             "<title>A short SEO title | Blog</title>")
        self.assertEqual(verify(self.read, REVISION), (ARTICLE, 3))

    def test_homepage_title_must_not_append_the_description(self):
        content, kind = self.files["/"]
        self.files["/"] = (content.replace(b"<title>Blog</title>",
                                          b"<title>Blog | Blog description</title>"), kind)
        with self.assertRaisesRegex(ValueError, "homepage title"):
            verify(self.read, REVISION)

    def test_indexed_pages_require_one_nonempty_h1(self):
        for path, heading in (("/", "Blog"), (ARTICLE, "A &amp; B")):
            content, kind = self.files[path]
            for replacement in ("", "<h1> </h1>", "<h1>First</h1><h1>Second</h1>"):
                with self.subTest(path=path, replacement=replacement):
                    self.files[path] = (
                        content.replace(f"<h1>{heading}</h1>".encode(), replacement.encode()), kind,
                    )
                    with self.assertRaisesRegex(ValueError, "one nonempty H1"):
                        verify(self.read, REVISION)
            self.files[path] = (content, kind)

    def test_article_requires_one_nonempty_browser_title(self):
        content, kind = self.files[ARTICLE]
        for replacement in ("", "<title> </title>", "<title>First</title><title>Second</title>"):
            with self.subTest(replacement=replacement):
                self.files[ARTICLE] = (
                    content.replace(b"<title>A &amp; B | Blog</title>", replacement.encode()), kind,
                )
                with self.assertRaisesRegex(ValueError, "one nonempty title"):
                    verify(self.read, REVISION)

    def test_mismatched_editorial_title_fails_even_with_a_matching_browser_title(self):
        self.replace_article('property="og:title" content="A &amp; B"',
                             'property="og:title" content="Wrong article"')
        with self.assertRaisesRegex(ValueError, "fallback"):
            verify(self.read, REVISION)

    def test_missing_or_conflicting_schema_headline_fails(self):
        content, kind = self.files[ARTICLE]
        for headline in ("", "Wrong article"):
            with self.subTest(headline=headline):
                self.files[ARTICLE] = (
                    content.replace(b'"headline": "A & B"',
                                    f'"headline": "{headline}"'.encode()), kind,
                )
                with self.assertRaisesRegex(ValueError, "headline"):
                    verify(self.read, REVISION)

    def test_heading_parser_preserves_nested_text_and_decodes_entities(self):
        page = Page(b"<title>A &amp; B</title><h1>A <em>&amp;</em> B</h1>")
        self.assertEqual(page.title, "A & B")
        self.assertEqual(page.title_count, 1)
        self.assertEqual(page.h1s, ["A & B"])

    def test_conflicting_canonical_fails(self):
        self.replace_article('rel="canonical"', 'rel="alternate"')
        with self.assertRaisesRegex(ValueError, "Canonical URL"):
            verify(self.read, REVISION)

    def test_missing_structured_data_fails(self):
        self.replace_article('type="application/ld+json"', 'type="application/json"')
        with self.assertRaisesRegex(ValueError, "structured data"):
            verify(self.read, REVISION)

    def test_missing_author_profile_fails(self):
        self.replace_article('"url": "https://example.test/about/"', '"url": ""')
        with self.assertRaisesRegex(ValueError, "profile URL"):
            verify(self.read, REVISION)

    def test_missing_social_image_fails(self):
        self.replace_article('property="og:image"', 'property="unused"')
        with self.assertRaisesRegex(ValueError, "image metadata"):
            verify(self.read, REVISION)

    def test_explicit_social_image_can_differ_from_banner(self):
        self.replace_article(ORIGIN + "assets/diagram.svg", ORIGIN + "assets/social.png")
        self.files["/assets/social.png"] = (b"png", "image/png")
        self.assertEqual(verify(self.read, REVISION), (ARTICLE, 3))

    def test_missing_description_fails(self):
        self.replace_article('name="description"', 'name="unused"')
        with self.assertRaisesRegex(ValueError, "description"):
            verify(self.read, REVISION)

    def test_noindex_article_fails(self):
        content, kind = self.files[ARTICLE]
        self.files[ARTICLE] = (content + b'<meta name="robots" content="noindex">', kind)
        with self.assertRaisesRegex(ValueError, "restricts indexing"):
            verify(self.read, REVISION)

    def test_search_crawler_block_fails(self):
        self.files["/robots.txt"] = (b"User-agent: OAI-SearchBot\nDisallow: /\n", "text/plain")
        with self.assertRaisesRegex(ValueError, "blocks OAI-SearchBot"):
            verify(self.read, REVISION)

    def test_stale_llm_index_fails(self):
        self.files["/llms.txt"] = (b"No articles yet", "text/plain")
        with self.assertRaisesRegex(ValueError, "missing from the generated LLM index"):
            verify(self.read, REVISION)

    def test_unpublished_link_in_llm_index_fails(self):
        content, kind = self.files["/llms.txt"]
        self.files["/llms.txt"] = (content + b"- [Draft](https://example.test/draft): hidden", kind)
        with self.assertRaisesRegex(ValueError, "does not match"):
            verify(self.read, REVISION)

    def test_missing_hub_link_fails(self):
        self.files["/fabric-spark/"] = (b"<p>Empty</p>", "text/html")
        with self.assertRaisesRegex(ValueError, "missing from the Fabric/Spark hub"):
            verify(self.read, REVISION)

    def test_sitemap_rejects_noncanonical_urls(self):
        for url in (ORIGIN + "article.html", "https://external.test/article", ORIGIN + "article?q=1"):
            with self.subTest(url=url):
                xml = (f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                       f"<url><loc>{url}</loc></url></urlset>").encode()
                with self.assertRaises(ValueError):
                    sitemap_urls(xml, ORIGIN)

    @patch("verify_site.urlopen")
    def test_http_reader_rejects_canonical_redirect(self, open_url):
        response = open_url.return_value.__enter__.return_value
        response.geturl.return_value = ORIGIN + "other"
        with self.assertRaisesRegex(ValueError, "resource redirects"):
            http_reader(ORIGIN)("/article")

    @patch("verify_site.urlopen")
    def test_http_reader_rejects_noindex_headers(self, open_url):
        response = open_url.return_value.__enter__.return_value
        response.geturl.return_value = ORIGIN + "article"
        response.headers.get_content_type.return_value = "text/html"
        response.headers.get.return_value = "noindex"
        with self.assertRaisesRegex(ValueError, "HTTP headers"):
            http_reader(ORIGIN)("/article")

    @patch("verify_site.urlopen")
    def test_live_routes_require_legacy_redirect_and_real_404(self, open_url):
        response = MagicMock()
        response.__enter__.return_value.geturl.return_value = ORIGIN.rstrip("/") + ARTICLE
        missing = HTTPError(ORIGIN + "missing", 404, "Not Found", {}, None)
        open_url.side_effect = [response, missing]
        verify_live_routes(ORIGIN, ARTICLE, REVISION)
        open_url.side_effect = [response, MagicMock()]
        with self.assertRaisesRegex(ValueError, "instead of HTTP 404"):
            verify_live_routes(ORIGIN, ARTICLE, REVISION)
        response.__enter__.return_value.geturl.return_value += ".html"
        open_url.side_effect = [response]
        with self.assertRaisesRegex(ValueError, "legacy"):
            verify_live_routes(ORIGIN, ARTICLE, REVISION)


if __name__ == "__main__":
    unittest.main()
