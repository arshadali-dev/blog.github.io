"""Notify IndexNow only after the expected production revision is publicly available."""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TypedDict
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from verify_site import Reader, http_reader, sitemap_urls

ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_FILE = Path(__file__).resolve().parents[2] / "indexnow-key.txt"


class Submission(TypedDict):
    host: str
    key: str
    keyLocation: str
    urlList: list[str]


def build_submission(
    read: Reader, origin: str, revision: str, expected_key: str,
    deleted_urls: tuple[str, ...] = (),
) -> Submission:
    origin = origin.rstrip("/")
    parsed = urlsplit(origin)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.path
            or parsed.query or parsed.fragment or parsed.username or parsed.port):
        raise ValueError("IndexNow requires a canonical HTTPS origin without a path or port")
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("The expected revision must be a full commit SHA")
    metadata, kind = read("/build-info.json")
    if kind != "application/json" or json.loads(metadata).get("revision") != revision:
        raise ValueError("The expected production revision is not live; not submitting")
    key_bytes, kind = read("/indexnow-key.txt")
    key = key_bytes.decode("utf-8").strip()
    if kind != "text/plain" or key != expected_key or not re.fullmatch(r"[a-zA-Z0-9-]{8,128}", key):
        raise ValueError("The public IndexNow ownership proof is invalid or does not match")
    urls = sitemap_urls(read("/sitemap.xml")[0], origin)
    for url in deleted_urls:
        target = urlsplit(url)
        if (target.scheme, target.netloc) != (parsed.scheme, parsed.netloc) or target.fragment:
            raise ValueError(f"Removed URL is not on the canonical origin: {url}")
        urls.append(url)
    urls = sorted(set(urls))
    if len(urls) > 10_000:
        raise ValueError("IndexNow accepts at most 10,000 URLs per submission")
    return {"host": parsed.netloc, "key": key,
            "keyLocation": origin + "/indexnow-key.txt", "urlList": urls}


def submit(payload: Submission) -> int:
    request = Request(
        ENDPOINT, data=json.dumps(payload).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "BlogDeploymentCheck"},
    )
    with urlopen(request, timeout=30) as response:
        status = response.status
        if status not in (200, 202):
            raise ValueError(f"IndexNow returned unexpected HTTP {status}")
        if response.headers.get_content_type() == "text/html":
            raise ValueError("IndexNow returned HTML instead of an API acknowledgement")
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--deleted-url", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        payload = build_submission(
            http_reader(args.url), args.url, args.revision,
            KEY_FILE.read_text(encoding="utf-8").strip(), tuple(args.deleted_url),
        )
        if args.dry_run:
            print(json.dumps({"host": payload["host"], "urlList": payload["urlList"]}, indent=2))
            return 0
        status = submit(payload)
    except (OSError, ValueError, ET.ParseError) as error:
        print(f"IndexNow submission failed: {error}", file=sys.stderr)
        return 1
    detail = "received" if status == 200 else "accepted pending key validation"
    print(f"IndexNow {detail}: {len(payload['urlList'])} URLs (HTTP {status}). "
          "This acknowledgement does not guarantee indexing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
