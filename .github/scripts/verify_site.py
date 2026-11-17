"""Verify built or deployed blog content without third-party dependencies."""

import argparse
import json
import mimetypes
import sys
import time
import xml.etree.ElementTree as ET
from collections.abc import Callable
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlsplit
from urllib.request import Request, urlopen

Reader = Callable[[str], tuple[bytes, str]]


class Page(HTMLParser):
    def __init__(self, content: bytes):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.links: list[str] = []
        self.assets: list[tuple[str, str]] = []
        self.in_title = False
        self.feed(content.decode("utf-8"))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "a" and (href := values.get("href")):
            self.links.append(href)
        if tag == "img" and (src := values.get("src")):
            self.assets.append((src, "image/"))
        if tag == "script" and (src := values.get("src")):
            self.assets.append((src, "javascript"))
        if tag == "link" and "stylesheet" in (values.get("rel") or "").split():
            if href := values.get("href"):
                self.assets.append((href, "text/css"))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data


def local_path(reference: str, base: str) -> str | None:
    target = urlsplit(urljoin(base, reference))
    origin = urlsplit(base)
    if (target.scheme, target.netloc) != (origin.scheme, origin.netloc):
        return None
    return quote(target.path or "/", safe="/%")


def directory_reader(directory: Path) -> Reader:
    root = directory.resolve()

    def read(path: str) -> tuple[bytes, str]:
        target = (root / unquote(path).lstrip("/")).resolve()
        if not target.is_relative_to(root):
            raise ValueError(f"Path escapes the build directory: {path}")
        if target.is_dir():
            target /= "index.html"
        content_type = mimetypes.guess_type(target.name)[0] or ""
        return target.read_bytes(), content_type

    return read


def http_reader(url: str) -> Reader:
    origin = urlsplit(url)
    if origin.scheme != "https" or not origin.netloc or origin.path not in ("", "/"):
        raise ValueError("The live site URL must be an HTTPS origin without a path")

    def read(path: str) -> tuple[bytes, str]:
        request = Request(
            url.rstrip("/") + path,
            headers={"Cache-Control": "no-cache", "User-Agent": "BlogDeploymentCheck"},
        )
        with urlopen(request, timeout=20) as response:
            final = urlsplit(response.geturl())
            if (final.scheme, final.netloc) != (origin.scheme, origin.netloc):
                raise ValueError(f"Unexpected cross-origin redirect for {path}")
            return response.read(), response.headers.get_content_type()

    return read


def verify(read: Reader, revision: str) -> tuple[str, int]:
    metadata, kind = read("/build-info.json")
    if kind != "application/json":
        raise ValueError("build-info.json is missing or returned a fallback page")
    if json.loads(metadata).get("revision") != revision:
        raise ValueError(f"The site is not serving expected revision {revision}")

    home_bytes, kind = read("/")
    if kind != "text/html":
        raise ValueError("The homepage is not HTML")
    home = Page(home_bytes)
    if not home.title.strip():
        raise ValueError("The homepage has no title")

    feed_bytes, _ = read("/feed.xml")
    feed = ET.fromstring(feed_bytes)
    origin = feed.findtext("./channel/link", "").strip()
    if urlsplit(origin).scheme not in ("http", "https") or not urlsplit(origin).netloc:
        raise ValueError("The feed has no valid canonical site URL")
    title = feed.findtext("./channel/item/title", "").strip()
    article_url = feed.findtext("./channel/item/link", "").strip()
    article_path = local_path(article_url, origin)
    if not title or not article_url or not article_path or article_path == "/":
        raise ValueError("The feed has no valid latest article on this site")
    if article_path not in {local_path(link, origin) for link in home.links}:
        raise ValueError(f"The latest article is missing from the homepage: {article_path}")

    article_bytes, kind = read(article_path)
    article = Page(article_bytes)
    if kind != "text/html" or not (
        article.title == title or article.title.startswith(title + " |")
    ):
        raise ValueError(f"The article is missing or returned a fallback page: {article_path}")

    sitemap_bytes, _ = read("/sitemap.xml")
    sitemap = ET.fromstring(sitemap_bytes)
    locations = {
        local_path(node.text or "", origin)
        for node in sitemap.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    }
    if article_path not in locations:
        raise ValueError("The latest article is missing from the sitemap")
    search_bytes, _ = read("/search/")
    if unquote(article_path) not in unquote(search_bytes.decode("utf-8")):
        raise ValueError("The latest article is missing from the search index")

    checked: set[str] = set()
    for page, base in ((home, origin), (article, article_url)):
        for reference, expected_type in page.assets:
            path = local_path(reference, base)
            if path is None or path in checked:
                continue
            content, kind = read(path)
            if not content or expected_type not in kind:
                raise ValueError(f"Asset missing, empty, or returned the wrong type: {path}")
            checked.add(path)
    if not checked:
        raise ValueError("No local assets were found to verify")
    return article_path, len(checked)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--directory", type=Path)
    source.add_argument("--url")
    parser.add_argument("--revision", required=True)
    parser.add_argument("--attempts", type=int, default=1)
    args = parser.parse_args()
    if args.attempts < 1:
        parser.error("--attempts must be at least 1")
    read = directory_reader(args.directory) if args.directory else http_reader(args.url)
    for attempt in range(1, args.attempts + 1):
        try:
            article, assets = verify(read, args.revision)
        except (OSError, ValueError, ET.ParseError) as error:
            print(f"Verification failed ({attempt}/{args.attempts}): {error}", file=sys.stderr)
            if attempt == args.attempts:
                return 1
            time.sleep(10)
        else:
            print(f"Verified {args.revision}: {article}, {assets} local assets.")
            return 0
    raise RuntimeError("No verification attempt was made")


if __name__ == "__main__":
    sys.exit(main())
