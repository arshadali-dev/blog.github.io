"""Offline tests for ownership, deployment gating and IndexNow acknowledgements."""

import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from submit_indexnow import ENDPOINT, build_submission, submit

ORIGIN = "https://example.test"
REVISION = "a" * 40
KEY = "b" * 32


class IndexNow(unittest.TestCase):
    def setUp(self):
        self.files = {
            "/build-info.json": (json.dumps({"revision": REVISION}).encode(), "application/json"),
            "/indexnow-key.txt": (KEY.encode(), "text/plain"),
            "/sitemap.xml": (
                (f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                 f"<url><loc>{ORIGIN}/</loc></url>"
                 f"<url><loc>{ORIGIN}/article</loc></url>"
                 f"<url><loc>{ORIGIN}/article</loc></url></urlset>").encode(),
                "application/xml",
            ),
        }

    def read(self, path):
        return self.files[path]

    def payload(self):
        return build_submission(self.read, ORIGIN, REVISION, KEY)

    def test_deduplicated_public_urls_and_key_location(self):
        self.assertEqual(self.payload(), {
            "host": "example.test", "key": KEY, "keyLocation": ORIGIN + "/indexnow-key.txt",
            "urlList": [ORIGIN + "/", ORIGIN + "/article"],
        })

    def test_stale_revision_is_not_submitted(self):
        with self.assertRaisesRegex(ValueError, "revision"):
            build_submission(self.read, ORIGIN, "c" * 40, KEY)
        with self.assertRaisesRegex(ValueError, "full commit SHA"):
            build_submission(self.read, ORIGIN, "short", KEY)

    def test_exact_submission_size_limit(self):
        for size in (10_000, 10_001):
            entries = "".join(f"<url><loc>{ORIGIN}/article-{i}</loc></url>" for i in range(size))
            self.files["/sitemap.xml"] = (
                ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                 + entries + "</urlset>").encode(), "application/xml",
            )
            if size == 10_000:
                self.assertEqual(len(self.payload()["urlList"]), size)
            else:
                with self.assertRaisesRegex(ValueError, "at most 10,000"):
                    self.payload()

    def test_missing_ownership_proof_fails(self):
        self.files["/indexnow-key.txt"] = (b"<html>fallback</html>", "text/html")
        with self.assertRaisesRegex(ValueError, "ownership"):
            self.payload()

    def test_mismatched_and_invalid_key_fail(self):
        with self.assertRaisesRegex(ValueError, "ownership"):
            build_submission(self.read, ORIGIN, REVISION, "different")
        self.files["/indexnow-key.txt"] = (b"short", "text/plain")
        with self.assertRaisesRegex(ValueError, "ownership"):
            build_submission(self.read, ORIGIN, REVISION, "short")

    def test_invalid_origin_fails(self):
        for origin in ("http://example.test", ORIGIN + "/path", ORIGIN + "?q=1"):
            with self.subTest(origin=origin), self.assertRaisesRegex(ValueError, "HTTPS origin"):
                build_submission(self.read, origin, REVISION, KEY)

    def test_removed_urls_must_belong_to_site(self):
        payload = build_submission(self.read, ORIGIN, REVISION, KEY, (ORIGIN + "/removed",))
        self.assertIn(ORIGIN + "/removed", payload["urlList"])
        with self.assertRaisesRegex(ValueError, "canonical origin"):
            build_submission(self.read, ORIGIN, REVISION, KEY, ("https://other.test/removed",))

    @patch("submit_indexnow.urlopen")
    def test_200_and_202_are_accepted_not_indexing_confirmation(self, open_url):
        response = open_url.return_value.__enter__.return_value
        response.headers.get_content_type.return_value = "application/json"
        for status in (200, 202):
            response.status = status
            self.assertEqual(submit(self.payload()), status)
        request = open_url.call_args.args[0]
        self.assertEqual(request.full_url, ENDPOINT)
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(json.loads(request.data), self.payload())

    @patch("submit_indexnow.urlopen")
    def test_errors_are_not_silently_accepted(self, open_url):
        open_url.side_effect = HTTPError(ENDPOINT, 429, "Too Many Requests", {}, None)
        with self.assertRaises(HTTPError):
            submit(self.payload())
        open_url.side_effect = None
        response = open_url.return_value.__enter__.return_value
        response.status = 204
        with self.assertRaisesRegex(ValueError, "unexpected HTTP"):
            submit(self.payload())
        response.status = 200
        response.headers.get_content_type.return_value = "text/html"
        with self.assertRaisesRegex(ValueError, "HTML"):
            submit(self.payload())


if __name__ == "__main__":
    unittest.main()
