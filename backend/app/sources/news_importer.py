from app.database.connection import SessionLocal
from app.database.models import NewsArticle
from app.sources.crunchyroll_news_client import CrunchyrollNewsClient


def import_crunchyroll_news(limit=25):
    client = CrunchyrollNewsClient()
    articles = client.fetch_news(limit=limit)

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
