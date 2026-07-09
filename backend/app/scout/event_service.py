from app.database.connection import SessionLocal
from app.database.models import NewsArticle
from app.scout.event_engine import ScoutEventEngine


class ScoutEventService:
    def get_events(self):
        db = SessionLocal()

        try:
            articles = (
                db.query(NewsArticle)
                .filter(NewsArticle.intelligence_event.isnot(None))
                .all()
            )

            return ScoutEventEngine().build_events(articles)

        finally:
            db.close()

    def get_events_for_anime(self, anime_name: str):
        events = self.get_events()
        target = anime_name.lower().strip()

        return [
            event
            for event in events
            if event.anime.lower().strip() == target
        ]
