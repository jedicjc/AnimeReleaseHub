import feedparser


class CrunchyrollNewsClient:
    FEED_URL = "https://www.crunchyroll.com/news/rss"

    def fetch_news(self, limit=25):
        feed = feedparser.parse(self.FEED_URL)

        articles = []

        for entry in feed.entries[:limit]:
            articles.append(
                {
                    "title": entry.get("title"),
                    "url": entry.get("link"),
                    "source": "Crunchyroll News",
                    "summary": entry.get("summary", ""),
                    "published_at": entry.get("published", None),
                }
            )

        return articles
