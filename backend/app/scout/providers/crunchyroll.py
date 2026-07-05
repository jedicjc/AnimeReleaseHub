from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from app.scout.config import REQUEST_TIMEOUT
from app.scout.sources import HEADERS


class CrunchyrollProvider:
    FEED_URL = "https://www.crunchyroll.com/news/rss"
    NEWS_URL = "https://www.crunchyroll.com/news"

    def fetch_news(self, limit=25):
        import feedparser

        diagnostics = {
            "requested_url": self.FEED_URL,
            "final_url": None,
            "status_code": None,
            "content_type": None,
            "bozo": False,
            "fallback_used": False,
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
            {
                "title": entry.get("title"),
                "url": entry.get("link"),
                "source": "Crunchyroll News",
                "summary": entry.get("summary", ""),
                "published_at": entry.get("published"),
            }
            for entry in feed.entries[:limit]
        ]

        if items:
            diagnostics["entries_found"] = len(items)
            return {
                "items": items,
                "diagnostics": diagnostics,
            }

        diagnostics["fallback_used"] = True
        html_response = requests.get(
            self.NEWS_URL,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        soup = BeautifulSoup(html_response.text, "html.parser")

        html_items = []
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
            html_items.append(
                {
                    "title": title,
                    "url": url,
                    "source": "Crunchyroll News",
                    "summary": "",
                    "published_at": None,
                }
            )

            if len(html_items) >= limit:
                break

        diagnostics["entries_found"] = len(html_items)
        diagnostics["final_url"] = html_response.url
        diagnostics["status_code"] = html_response.status_code
        diagnostics["content_type"] = html_response.headers.get("content-type")

        return {
            "items": html_items,
            "diagnostics": diagnostics,
        }
