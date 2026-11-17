"""Verify built or deployed blog content without third-party dependencies."""

import argparse
import json
import mimetypes
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections.abc import Callable
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlsplit
from urllib.error import HTTPError
from urllib.robotparser import RobotFileParser
from urllib.request import Request, urlopen

Reader = Callable[[str], tuple[bytes, str]]


class Page(HTMLParser):
    def __init__(self, content: bytes):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.title_count = 0
        self.h1s: list[str] = []
        self.in_h1 = False
        self.links: list[str] = []
        self.assets: list[tuple[str, str]] = []
        self.canonicals: list[str] = []
        self.meta: dict[str, str] = {}
        self.schemas: list[dict[str, object]] = []
        self.feature_image = ""
        self.has_related_guides = False
        self.in_schema = False
        self.schema_text = ""
        self.in_title = False
        self.feed(content.decode("utf-8"))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "title":
            self.in_title = True
            self.title_count += 1
        if tag == "h1":
            self.h1s.append("")
            self.in_h1 = True
        if tag == "a" and (href := values.get("href")):
            self.links.append(href)
        if tag == "nav" and values.get("aria-label") == "Related guides":
            self.has_related_guides = True
        if tag == "img" and (src := values.get("src")):
            self.assets.append((src, "image/"))
            if "feature-img" in (values.get("class") or "").split():
                self.feature_image = src
        if tag == "meta" and (name := values.get("name") or values.get("property")):
            self.meta[name] = values.get("content") or ""
        if tag == "link" and values.get("rel") == "canonical":
            self.canonicals.append(values.get("href") or "")
        if tag == "script" and values.get("type") == "application/ld+json":
            self.in_schema = True
            self.schema_text = ""
        if tag == "script" and (src := values.get("src")):
            self.assets.append((src, "javascript"))
        if tag == "link" and "stylesheet" in (values.get("rel") or "").split():
            if href := values.get("href"):
                self.assets.append((href, "text/css"))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if tag == "h1":
            self.in_h1 = False
        if tag == "script" and self.in_schema:
            schema = json.loads(self.schema_text)
            if not isinstance(schema, dict):
                raise ValueError("Structured data must be a JSON object")
            self.schemas.append(schema)
            self.in_schema = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data
        if self.in_h1:
            self.h1s[-1] += data
        if self.in_schema:
            self.schema_text += data


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
        elif not target.exists() and not target.suffix:
            target = target.with_suffix(".html")
        target = target.resolve()
        if not target.is_relative_to(root):
            raise ValueError(f"Path escapes the build directory: {path}")
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
            if unquote(final.path) != unquote(path):
                raise ValueError(f"Canonical resource redirects: {path} -> {final.path}")
            if response.headers.get_content_type() == "text/html":
                directives = response.headers.get("X-Robots-Tag", "").lower()
                if any(token in directives for token in ("noindex", "none", "nosnippet")):
                    raise ValueError(f"HTTP headers restrict indexing or snippets: {path}")
            return response.read(), response.headers.get_content_type()

    return read


def sitemap_urls(content: bytes, origin: str) -> list[str]:
    root = ET.fromstring(content)
    if root.tag != "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset":
        raise ValueError("Expected a sitemap URL set")
    urls: set[str] = set()
    for node in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
        url = (node.text or "").strip()
        target = urlsplit(url)
        path = local_path(url, origin)
        if not url.startswith(origin.rstrip("/") + "/") or path is None:
            raise ValueError(f"Sitemap URL is not on the canonical origin: {url}")
        if target.query or target.fragment or path.endswith(".html"):
            raise ValueError(f"Sitemap URL is not canonical: {url}")
        urls.add(origin.rstrip("/") + path)
    if not urls:
        raise ValueError("The sitemap has no URLs")
    return sorted(urls)


def verify_discovery(read: Reader, origin: str) -> None:
    origin = origin.rstrip("/") + "/"
    urls = sitemap_urls(read("/sitemap.xml")[0], origin)
    llms, kind = read("/llms.txt")
    if kind != "text/plain":
        raise ValueError("The LLM index is missing or returned a fallback page")
    llms_text = llms.decode("utf-8")
    robots = RobotFileParser()
    robots.parse(read("/robots.txt")[0].decode("utf-8").splitlines())
    hub = Page(read("/fabric-spark/")[0])
    hub_links = {local_path(link, origin) for link in hub.links}
    posts: set[str] = set()
    for url in urls:
        path = local_path(url, origin)
        if path is None:
            raise ValueError(f"Non-local sitemap URL: {url}")
        content, kind = read(path)
        page = Page(content)
        if kind != "text/html" or page.canonicals != [url]:
            raise ValueError(f"Canonical URL does not match the sitemap: {url}")
        if page.title_count != 1 or not page.title.strip():
            raise ValueError(f"Sitemap page must have one nonempty title: {url}")
        if len(page.h1s) != 1 or not page.h1s[0].strip():
            raise ValueError(f"Sitemap page must have one nonempty H1: {url}")
        if not page.meta.get("description"):
            raise ValueError(f"Missing page description: {url}")
        directives = page.meta.get("robots", "").lower()
        if any(token in directives for token in ("noindex", "none", "nosnippet")):
            raise ValueError(f"Sitemap page restricts indexing or snippets: {url}")
        for bot in ("Googlebot", "bingbot", "OAI-SearchBot"):
            if not robots.can_fetch(bot, url):
                raise ValueError(f"robots.txt blocks {bot}: {url}")
        schemas = [schema for schema in page.schemas if schema.get("@type") == "BlogPosting"]
        if page.meta.get("og:type") == "article" and not schemas:
            raise ValueError(f"Article structured data is missing: {url}")
        for schema in schemas:
            posts.add(url)
            if schema.get("url") != url or page.meta.get("og:url") != url:
                raise ValueError(f"Article metadata has a conflicting URL: {url}")
            if not schema.get("headline") or schema["headline"] != page.meta.get("og:title"):
                raise ValueError(f"Article metadata has a missing or conflicting headline: {url}")
            author = schema.get("author")
            if not isinstance(author, dict) or not author.get("name") or not author.get("url"):
                raise ValueError(f"Article author has no name or profile URL: {url}")
            if not schema.get("datePublished") or not schema.get("dateModified"):
                raise ValueError(f"Article dates are missing: {url}")
            if f"]({url}):" not in llms_text:
                raise ValueError(f"Article is missing from the generated LLM index: {url}")
            if page.has_related_guides:
                if path not in hub_links:
                    raise ValueError(f"Article is missing from the Fabric/Spark hub: {url}")
            if page.feature_image:
                image = page.meta.get("og:image", "")
                schema_image = schema.get("image")
                if isinstance(schema_image, dict):
                    schema_image = schema_image.get("url")
                if (urlsplit(image).scheme != "https"
                        or page.meta.get("twitter:image") != image
                        or schema_image != image):
                    raise ValueError(f"Article banner is missing from SEO image metadata: {url}")
                image_path = local_path(image, origin)
                if image_path is not None:
                    image_bytes, image_type = read(image_path)
                    if not image_bytes or not image_type.startswith("image/"):
                        raise ValueError(f"Invalid SEO image: {image}")
    listed = set(re.findall(r"^- \[.*\]\((https://[^\s)]+)\):", llms_text, re.MULTILINE))
    if listed != posts:
        raise ValueError("The LLM index does not match the published sitemap articles")
    missing, kind = read("/404")
    if kind != "text/html" or "noindex" not in Page(missing).meta.get("robots", ""):
        raise ValueError("The custom 404 page must be HTML with noindex")


def verify_live_routes(origin: str, article: str, revision: str) -> None:
    headers = {"Cache-Control": "no-cache", "User-Agent": "BlogDeploymentCheck"}
    expected = origin.rstrip("/") + article
    with urlopen(Request(expected + ".html", headers=headers), timeout=20) as response:
        if unquote(response.geturl()) != unquote(expected):
            raise ValueError("The legacy .html article URL does not redirect to its canonical URL")
    missing = origin.rstrip("/") + f"/__missing-deployment-check-{revision}"
    try:
        with urlopen(Request(missing, headers=headers), timeout=20):
            raise ValueError("A nonexistent URL returned success instead of HTTP 404")
    except HTTPError as error:
        error.close()
        if error.code != 404:
            raise ValueError(f"A nonexistent URL returned HTTP {error.code}, not 404") from error


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
    if home.title.strip() != feed.findtext("./channel/title", "").strip():
        raise ValueError("The homepage title does not match the feed's site title")
    title = feed.findtext("./channel/item/title", "").strip()
    article_url = feed.findtext("./channel/item/link", "").strip()
    article_path = local_path(article_url, origin)
    if not title or not article_url or not article_path or article_path == "/":
        raise ValueError("The feed has no valid latest article on this site")
    if article_path not in {local_path(link, origin) for link in home.links}:
        raise ValueError(f"The latest article is missing from the homepage: {article_path}")

    article_bytes, kind = read(article_path)
    article = Page(article_bytes)
    if (kind != "text/html" or article.meta.get("og:type") != "article"
            or article.meta.get("og:title") != title):
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
    verify_discovery(read, origin)
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
            if args.url:
                verify_live_routes(args.url, article, args.revision)
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
