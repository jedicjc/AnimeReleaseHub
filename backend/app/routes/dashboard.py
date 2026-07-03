from fastapi import APIRouter
from app.database.connection import SessionLocal
from app.database.models import Anime, NewsArticle
from app.maple.insight_engine import MapleInsightEngine
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/")
def dashboard():
    db = SessionLocal()

    try:
        service = DashboardService(db)
        trending = service.trending()
        highest_rated = service.highest_rated()
        latest_news = service.latest_news()
        upcoming = service.upcoming()
        maple_picks = service.maple_picks()
        engine = MapleInsightEngine(
            dashboard={
                "trending": trending,
                "highest_rated": highest_rated,
                "latest_news": latest_news,
            }
        )

        return {
            "trending": trending,
            "highest_rated": highest_rated,
            "latest_news": latest_news,
            "upcoming": upcoming,
            "maple_picks": maple_picks,
            "insight": engine.dashboard_insight(),
            "stats": {
                "anime": db.query(Anime).count(),
                "news": db.query(NewsArticle).count(),
                "trending": len(trending),
                "maple_picks": len(maple_picks),
            },
        }

    finally:
        db.close()
