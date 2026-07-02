from app.database.connection import SessionLocal
from app.database.models import Anime


def generate_explanation(anime_id: int):
    db = SessionLocal()

    try:
        anime = db.query(Anime).filter(Anime.id == anime_id).first()

        if not anime:
            return None

        reasons = []

        # -------------------------
        # GENRE SIGNAL
        # -------------------------
        if anime.genres:
            genres = anime.genres.split(",")

            if len(genres) >= 3:
                reasons.append("Strong multi-genre appeal increases audience reach")
            else:
                reasons.append("Focused genre identity improves targeting")

        # -------------------------
        # SCORE SIGNAL
        # -------------------------
        if anime.score:
            if anime.score >= 8:
                reasons.append("High user rating indicates strong community approval")
            elif anime.score >= 6:
                reasons.append("Moderate rating suggests niche appeal")
            else:
                reasons.append("Low rating but potential cult interest")

        # -------------------------
        # STATUS SIGNAL
        # -------------------------
        if anime.status == "announced":
            reasons.append("New announcement is driving early hype spike")
        elif anime.status == "ongoing":
            reasons.append("Active airing increases visibility and engagement")

        # -------------------------
        # TREND SIGNAL
        # -------------------------
        if anime.created_at:
            reasons.append("Recent listing boosts algorithmic visibility")

        return {
            "id": anime.id,
            "title": anime.title,
            "explanation": reasons,
        }

    finally:
        db.close()
