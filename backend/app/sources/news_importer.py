from app.database.connection import SessionLocal
from app.database.models import NewsArticle
from app.sources.crunchyroll_news_client import CrunchyrollNewsClient
from app.sources.hidive_news_client import HidiveNewsClient


def save_news_articles(articles):
    db = SessionLocal()
    imported = 0

    try:
        for item in articles:
            if not item.get("url"):
                continue

            existing = (
                db.query(NewsArticle).filter(NewsArticle.url == item["url"]).first()
            )

            if existing:
                continue

            article = NewsArticle(
                title=item.get("title"),
                url=item.get("url"),
                source=item.get("source"),
                summary=item.get("summary"),
            )

            db.add(article)
            imported += 1

        db.commit()

        return imported

    finally:
        db.close()


def import_crunchyroll_news(limit=25):
    client = CrunchyrollNewsClient()
    return save_news_articles(client.fetch_news(limit=limit))


def import_hidive_news(limit=25):
    client = HidiveNewsClient()
    return save_news_articles(client.fetch_news(limit=limit))
