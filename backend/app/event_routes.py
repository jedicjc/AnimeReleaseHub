from fastapi import APIRouter

from app.database.connection import SessionLocal
from app.database.models import NewsArticle
from app.news_utils import is_valid_news_title
from app.scout.event_engine import ScoutEventEngine

router = APIRouter(
    prefix="/events",
    tags=["Scout Events"],
)


@router.get("/")
def get_events():
    db = SessionLocal()

    try:
        articles = db.query(NewsArticle).all()
        articles = [
            article
            for article in articles
            if is_valid_news_title(getattr(article, "title", None))
        ]

        return ScoutEventEngine().build_events(articles)

    finally:
        db.close()
