class CrunchyrollProvider:
    FEED_URL = "https://www.crunchyroll.com/news/rss"

    def fetch_news(self, limit=25):
        import feedparser

        feed = feedparser.parse(self.FEED_URL)

        return [
            {
                "title": entry.get("title"),
                "url": entry.get("link"),
                "source": "Crunchyroll News",
                "summary": entry.get("summary", ""),
                "published_at": entry.get("published"),
            }
            for entry in feed.entries[:limit]
        ]
