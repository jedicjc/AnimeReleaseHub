from app.database.connection import SessionLocal
from app.database.models import Anime
from app.maple.trends import calculate_trend_score


def get_dashboard_data():
    db = SessionLocal()

    try:
        anime_list = db.query(Anime).all()

        rising = []
        stable = []
        cooling = []

        total_trend = 0

        for a in anime_list:
            score = calculate_trend_score(a)
            total_trend += score

            item = {
                "id": a.id,
                "title": a.title,
                "poster_url": a.poster_url,
                "trend_score": round(score, 2),
            }

            if score >= 120:
                rising.append(item)
            elif score >= 70:
                stable.append(item)
            else:
                cooling.append(item)

        return {
            "summary": {
                "total_anime": len(anime_list),
                "average_trend": round(total_trend / len(anime_list), 2)
                if anime_list
                else 0,
            },
            "rising": sorted(
                rising, key=lambda x: x["trend_score"], reverse=True
            )[:5],
            "stable": sorted(
                stable, key=lambda x: x["trend_score"], reverse=True
            )[:5],
            "cooling": sorted(
                cooling, key=lambda x: x["trend_score"], reverse=True
            )[:5],
        }

    finally:
        db.close()
