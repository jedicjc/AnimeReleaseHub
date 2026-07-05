class HidiveProvider:
    FEED_URL = "https://news.hidive.com/rss"

    def fetch_news(self, limit=25):
        import feedparser

        feed = feedparser.parse(self.FEED_URL)

        return [
            {
                "title": entry.get("title"),
                "url": entry.get("link"),
                "source": "HIDIVE News",
                "summary": entry.get("summary", ""),
                "published_at": entry.get("published"),
            }
            for entry in feed.entries[:limit]
        ]
