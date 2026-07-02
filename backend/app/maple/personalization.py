from app.database.connection import SessionLocal
from app.database.models import Anime


def build_user_profile(favorite_genres: list[str]):
    """
    Simulated user preference model
    (later replaced with real watch history)
    """

    return {
        "favorite_genres": set([g.lower() for g in favorite_genres]),
        "weight_genre": 3,
        "weight_score": 2,
        "weight_recency": 1,
    }


def score_for_user(anime, profile):
    score = 0
    reasons = []

    anime_genres = set((anime.genres or "").lower().split(","))

    # -------------------------
    # GENRE MATCH (STRONG SIGNAL)
    # -------------------------
    common = anime_genres.intersection(profile["favorite_genres"])

    if common:
        score += len(common) * profile["weight_genre"]
        reasons.append(f"Matches your interest in {', '.join(common)}")

    # -------------------------
    # HIGH SCORE BOOST
    # -------------------------
    if anime.score:
        score += anime.score * profile["weight_score"]

        if anime.score >= 8:
            reasons.append("Highly rated anime aligns with your taste")

    # -------------------------
    # RECENCY BOOST
    # -------------------------
    if anime.status in ["announced", "ongoing"]:
        score += 5
        reasons.append("Active or upcoming anime keeps you updated")

    return score, reasons


def get_personalized_recommendations(favorite_genres: list[str], limit: int = 10):
    db = SessionLocal()

    try:
        profile = build_user_profile(favorite_genres)

        all_anime = db.query(Anime).all()

        results = []

        for a in all_anime:
            score, reasons = score_for_user(a, profile)

            if score <= 0:
                continue

            results.append(
                {
                    "id": a.id,
                    "title": a.title,
                    "poster_url": a.poster_url,
                    "personal_score": round(score, 2),
                    "why": reasons[:3],
                }
            )

        results.sort(key=lambda x: x["personal_score"], reverse=True)

        return results[:limit]

    finally:
        db.close()
