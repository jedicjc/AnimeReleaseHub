from sqlalchemy.orm import Session

from app.database.models import Anime


class MapleComparisonEngine:
    def __init__(self, db: Session):
        self.db = db

    def find_titles(self, question: str):
        anime = self.db.query(Anime).all()

        matches = []
        q = question.lower()

        for item in anime:
            title = (item.title or "").lower()

            if title and title in q:
                matches.append(item)

        return matches[:2]
