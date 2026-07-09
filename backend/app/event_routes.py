from fastapi import APIRouter

from app.database.connection import SessionLocal
from app.database.models import NewsArticle
from app.scout.event_engine import ScoutEventEngine

router = APIRouter(
    prefix="/events",
    tags=["Scout Events"],
)


@router.get("/")
def get_events():
    db = SessionLocal()

    try:
        articles = (
            db.query(NewsArticle)
            .filter(NewsArticle.intelligence_event.isnot(None))
            .all()
        )

        events = ScoutEventEngine().build_events(articles)

        return events

    finally:
        db.close()
