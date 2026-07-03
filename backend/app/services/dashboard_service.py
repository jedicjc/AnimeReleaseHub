from app.database.models import Anime, NewsArticle
from app.maple.scoring import calculate_maple_score


class DashboardService:
    def __init__(self, db):
        self.db = db

    def trending(self, limit=10):
        return (
            self.db.query(Anime)
            .order_by(Anime.trend_score.desc())
            .limit(limit)
            .all()
        )

    def highest_rated(self, limit=10):
        return (
            self.db.query(Anime)
            .filter(Anime.score != None)
            .order_by(Anime.score.desc())
            .limit(limit)
            .all()
        )

    def latest_news(self, limit=10):
        return (
            self.db.query(NewsArticle)
            .order_by(NewsArticle.created_at.desc())
            .limit(limit)
            .all()
        )

    def upcoming(self, limit=10):
        return (
            self.db.query(Anime)
            .filter(Anime.status == "upcoming")
            .order_by(Anime.release_year.desc())
            .limit(limit)
            .all()
        )

    def maple_picks(self, limit=3):
        anime = self.db.query(Anime).all()

        ranked = sorted(
            anime,
            key=lambda a: calculate_maple_score(a),
            reverse=True,
        )

        return ranked[:limit]
