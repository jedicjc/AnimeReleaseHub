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

        return {
            "news_count": news_count,
            "anime_count": anime_count,
            "dub_count": 0,
            "latest_news": latest_news,
        }
    finally:
        db.close()