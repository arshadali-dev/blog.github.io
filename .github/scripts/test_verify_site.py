"""Regression tests for deployment checks, including Cloudflare's HTTP-200 fallback."""

import json
import tempfile
import unittest
from pathlib import Path

from verify_site import directory_reader, local_path, verify

REVISION = "a" * 40
ARTICLE = "/product%20management/2026/11/14/guide.html"
ORIGIN = "https://example.test/"


class VerifySite(unittest.TestCase):
    def setUp(self):
        self.files = {
            "/build-info.json": (
                json.dumps({"revision": REVISION}).encode(), "application/json",
            ),
            "/": (
                f'<title>Blog</title><a href="{ARTICLE}">Guide</a>'.encode(), "text/html",
            ),
            "/feed.xml": (
                f"<rss><channel><link>{ORIGIN}</link><item><title>A &amp; B</title>"
                f"<link>{ORIGIN.rstrip('/')}{ARTICLE}</link></item></channel></rss>".encode(),
                "application/xml",
            ),
            ARTICLE: (
                b'<title>A &amp; B | Blog</title><img src="/assets/diagram.svg">'
                b'<link rel="stylesheet" href="/assets/site.css">'
                b'<script src="/assets/site.js"></script>'
                b'<img src="https://external.test/image.png">',
                "text/html",
            ),
            "/sitemap.xml": (
                f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                f"<url><loc>{ORIGIN.rstrip('/')}{ARTICLE}</loc></url></urlset>".encode(),
                "application/xml",
            ),
            "/search/": (ARTICLE.encode(), "text/html"),
            "/assets/diagram.svg": (b"<svg/>", "image/svg+xml"),
            "/assets/site.css": (b"body {}", "text/css"),
            "/assets/site.js": (b"console.log('ok')", "text/javascript"),
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
            f"<rss><channel><link>{ORIGIN}</link></channel></rss>".encode(),
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
            read = directory_reader(root)
            self.assertEqual(read("/product%20management/"), (b"ok", "text/html"))
            with self.assertRaisesRegex(ValueError, "escapes"):
                read("/%2e%2e/outside.html")


if __name__ == "__main__":
    unittest.main()
