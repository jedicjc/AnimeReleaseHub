from fastapi import APIRouter
from app.database.connection import SessionLocal
from app.database.models import Anime, NewsArticle

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/")
def dashboard_summary():
    db = SessionLocal()

    try:
        news_count = db.query(NewsArticle).count()
        anime_count = db.query(Anime).count()

        latest_news = (
            db.query(NewsArticle)
            .order_by(NewsArticle.created_at.desc())
            .limit(6)
            .all()
        )

        all_articles = db.query(NewsArticle).all()

        category_counts = {}

        for article in all_articles:
            category = article.category or "general"
            category_counts[category] = category_counts.get(category, 0) + 1

        return {
            "news_count": news_count,
            "anime_count": anime_count,
            "dub_count": category_counts.get("dub_update", 0),
            "latest_news": latest_news,
            "category_counts": category_counts,
        }
    finally:
        db.close()