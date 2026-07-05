import re
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from app.scout.config import REQUEST_TIMEOUT
from app.scout.sources import HEADERS


class HidiveProvider:
    FEED_URL = "https://news.hidive.com/rss"
    NEWS_URL = "https://news.hidive.com/"
    SITEMAP_URLS = [
        "https://news.hidive.com/sitemap.xml",
        "https://news.hidive.com/news-sitemap.xml",
        "https://news.hidive.com/sitemap_index.xml",
    ]

    def _build_item(self, title, url, summary="", published_at=None):
        return {
            "title": title,
            "url": url,
            "source": "HIDIVE News",
            "summary": summary,
            "published_at": published_at,
        }

    def _title_from_url(self, url):
        slug = urlparse(url).path.rstrip("/").split("/")[-1]

        if not slug:
            return url

        return slug.replace("-", " ").replace("_", " ").strip()

    def _looks_like_article_url(self, url):
        parsed = urlparse(url)
        path = parsed.path.rstrip("/")

        if "hidive.com" not in parsed.netloc:
            return False

        if path in {"", "/"}:
            return False

        if path in {"/rss", "/feed"}:
            return False

        if any(
            path.endswith(ext)
            for ext in (".css", ".js", ".png", ".jpg", ".jpeg", ".svg", ".webp", ".ico")
        ):
            return False

        return len(path.split("/")) >= 2

    def _clean_candidate_url(self, raw_url):
        return raw_url.strip().strip("\"'").rstrip("),")

    def _collect_html_candidates(self, html_text, base_url):
        soup = BeautifulSoup(html_text, "html.parser")
        candidates = []
        seen = set()

        def add_candidate(raw_url, raw_title=""):
            if not raw_url:
                return

            url = urljoin(base_url, self._clean_candidate_url(raw_url))

            if not self._looks_like_article_url(url):
                return

            if url in seen:
                return

            seen.add(url)
            title = (raw_title or "").strip() or self._title_from_url(url)
            candidates.append(self._build_item(title=title, url=url))

        for link in soup.select("a[href], link[href]"):
            href = link.get("href")
            title = (
                link.get_text(" ", strip=True)
                or link.get("title")
                or link.get("aria-label")
                or link.get("data-title")
                or ""
            )
            add_candidate(href, title)

        for match in re.findall(r'https?://[^"\'>\s]+', html_text):
            add_candidate(match)

        for match in re.findall(r'/[A-Za-z0-9][^"\'>\s]+', html_text):
            add_candidate(match)

        return candidates

    def _extract_sitemap_urls(self, xml_text):
        root = ET.fromstring(xml_text)
        urls = []

        for node in root.iter():
            if node.tag.endswith("loc") and node.text:
                urls.append(node.text.strip())

        return urls

    def _fetch_sitemap_items(self, limit):
        items = []
        seen_urls = set()

        for sitemap_url in self.SITEMAP_URLS:
            try:
                response = requests.get(
                    sitemap_url,
                    headers=HEADERS,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True,
                )
            except requests.RequestException:
                continue

            if response.status_code != 200:
                continue

            try:
                sitemap_urls = self._extract_sitemap_urls(response.text)
            except ET.ParseError:
                continue

            for url in sitemap_urls:
                parsed = urlparse(url)

                if "hidive.com" not in parsed.netloc:
                    continue

                if url in seen_urls:
                    continue

                seen_urls.add(url)
                title = parsed.path.rstrip("/").split("/")[-1].replace("-", " ").strip()
                items.append(self._build_item(title=title or url, url=url))

                if len(items) >= limit:
                    return items, response

        return items, None

    def _fetch_html_items(self, limit):
        response = requests.get(
            self.NEWS_URL,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        items = self._collect_html_candidates(response.text, response.url)[:limit]

        return items, response

    def fetch_news(self, limit=25):
        import feedparser

        diagnostics = {
            "requested_url": self.FEED_URL,
            "final_url": None,
            "status_code": None,
            "content_type": None,
            "bozo": False,
            "fallback_used": False,
            "fallback_stage": None,
            "entries_found": 0,
            "error": None,
        }

        try:
            response = requests.get(
                self.FEED_URL,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            diagnostics["final_url"] = response.url
            diagnostics["status_code"] = response.status_code
            diagnostics["content_type"] = response.headers.get("content-type")

            feed = feedparser.parse(response.content)
            diagnostics["bozo"] = bool(getattr(feed, "bozo", False))

            items = [
                self._build_item(
                    title=entry.get("title"),
                    url=entry.get("link"),
                    summary=entry.get("summary", ""),
                    published_at=entry.get("published"),
                )
                for entry in feed.entries[:limit]
            ]

            if items:
                diagnostics["entries_found"] = len(items)
                return {"items": items, "diagnostics": diagnostics}

            diagnostics["fallback_used"] = True

            sitemap_items, sitemap_response = self._fetch_sitemap_items(limit)

            if sitemap_items:
                diagnostics["fallback_stage"] = "sitemap"
                diagnostics["entries_found"] = len(sitemap_items)
                if sitemap_response is not None:
                    diagnostics["final_url"] = sitemap_response.url
                    diagnostics["status_code"] = sitemap_response.status_code
                    diagnostics["content_type"] = sitemap_response.headers.get(
                        "content-type"
                    )
                return {"items": sitemap_items, "diagnostics": diagnostics}

            html_items, html_response = self._fetch_html_items(limit)
            diagnostics["fallback_stage"] = "html"
            diagnostics["entries_found"] = len(html_items)
            diagnostics["final_url"] = html_response.url
            diagnostics["status_code"] = html_response.status_code
            diagnostics["content_type"] = html_response.headers.get("content-type")

            return {"items": html_items, "diagnostics": diagnostics}
        except Exception as error:
            diagnostics["error"] = repr(error)
            return {"items": [], "diagnostics": diagnostics}
