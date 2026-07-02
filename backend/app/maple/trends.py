from app.database.connection import SessionLocal
from app.database.models import Anime
from datetime import datetime, timedelta


def category_weight(category: str | None) -> int:
    if category == "trailer":
        return 25
    if category == "sequel":
        return 22
    if category == "new_adaptation":
        return 20
    if category == "cast_update":
        return 12
    if category == "staff_update":
        return 10
    if category == "dub_update":
        return 8
    if category == "delay":
        return -10

    return 5


def calculate_trend_score(anime_or_category, anime_score: float | None = None):
    """
    Simple but powerful heuristic trend engine
    (can later upgrade to real analytics / ML)
    """

    if isinstance(anime_or_category, str) or anime_or_category is None:
        score = category_weight(anime_or_category)

        if anime_score:
            score += anime_score * 5

        return round(max(score, 0), 2)

    anime = anime_or_category
    score = 0

    # base popularity
    if anime.score:
        score += anime.score * 10

    # status boosts
    if anime.status == "announced":
        score += 20
    elif anime.status == "ongoing":
        score += 10

    # recency boost (if created recently)
    if anime.created_at:
        age_days = (datetime.utcnow() - anime.created_at).days

        if age_days < 7:
            score += 25
        elif age_days < 30:
            score += 10
        else:
            score += 2

    return score


def get_trending_anime(limit: int = 10):
    db = SessionLocal()

    try:
        all_anime = db.query(Anime).all()

        results = []

        for a in all_anime:
            trend = calculate_trend_score(a)

            # classify trend state
            if trend >= 120:
                label = "🔥 Rising Fast"
            elif trend >= 80:
                label = "📈 Trending"
            elif trend >= 50:
                label = "📊 Stable"
            else:
                label = "❄️ Cooling"

            results.append({
                "id": a.id,
                "title": a.title,
                "poster_url": a.poster_url,
                "trend_score": round(trend, 2),
                "trend_label": label
            })

        results.sort(key=lambda x: x["trend_score"], reverse=True)

        return results[:limit]

    finally:
        db.close()
