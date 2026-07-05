from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from app.scout.config import REQUEST_TIMEOUT
from app.scout.sources import HEADERS


class CrunchyrollProvider:
    FEED_URL = "https://www.crunchyroll.com/news/rss"
    NEWS_URL = "https://www.crunchyroll.com/news"
    SITEMAP_URLS = [
        "https://www.crunchyroll.com/sitemap.xml",
        "https://www.crunchyroll.com/news-sitemap.xml",
        "https://www.crunchyroll.com/news/sitemap.xml",
    ]

    def _build_item(self, title, url, summary="", published_at=None):
        return {
            "title": title,
            "url": url,
            "source": "Crunchyroll News",
            "summary": summary,
            "published_at": published_at,
        }

    def _fetch_sitemap_items(self, limit):
        items = []
        seen_urls = set()

        for sitemap_url in self.SITEMAP_URLS:
            response = requests.get(
                sitemap_url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )

            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "xml")

            for node in soup.find_all("url"):
                loc = node.find("loc")

                if not loc or not loc.text:
                    continue

                url = loc.text.strip()
                parsed = urlparse(url)

                if "crunchyroll.com" not in parsed.netloc:
                    continue

                if "/news" not in parsed.path:
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
        soup = BeautifulSoup(response.text, "html.parser")

        items = []
        seen_urls = set()

        for link in soup.select("article a[href], h1 a[href], h2 a[href], h3 a[href]"):
            href = link.get("href")
            title = link.get_text(" ", strip=True)

            if not href or len(title) < 8:
                continue

            url = urljoin(self.NEWS_URL, href)
            parsed = urlparse(url)

            if "crunchyroll.com" not in parsed.netloc:
                continue

            if "/news" not in parsed.path:
                continue

            if url in seen_urls:
                continue

            seen_urls.add(url)
            items.append(self._build_item(title=title, url=url))

            if len(items) >= limit:
                break

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
        }

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
                diagnostics["content_type"] = sitemap_response.headers.get("content-type")
            return {"items": sitemap_items, "diagnostics": diagnostics}

        html_items, html_response = self._fetch_html_items(limit)
        diagnostics["fallback_stage"] = "html"
        diagnostics["entries_found"] = len(html_items)
        diagnostics["final_url"] = html_response.url
        diagnostics["status_code"] = html_response.status_code
        diagnostics["content_type"] = html_response.headers.get("content-type")

        return {"items": html_items, "diagnostics": diagnostics}
