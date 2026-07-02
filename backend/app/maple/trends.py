from app.database.connection import SessionLocal
from app.database.models import Anime
from datetime import datetime, timedelta


def calculate_trend_score(anime):
    """
    Simple but powerful heuristic trend engine
    (can later upgrade to real analytics / ML)
    """

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