from fastapi import APIRouter
from datetime import datetime

from app.database.connection import SessionLocal
from app.database.models import Anime, AnimeTrendHistory

router = APIRouter(prefix="/trending", tags=["Trending"])


# -----------------------------
# TREND SCORE CALCULATION
# -----------------------------
def calculate_trend_score(anime: Anime):
    score = 0

    if anime.score:
        score += anime.score * 10

    if anime.poster_url:
        score += 20

    if anime.status == "upcoming":
        score += 15

    if anime.release_year:
        score += anime.release_year

    return score


# -----------------------------
# HISTORY SNAPSHOT
# -----------------------------
def save_trend_snapshot(db, anime_id: int, score: float):
    snapshot = AnimeTrendHistory(
        anime_id=anime_id,
        trend_score=score,
        created_at=datetime.utcnow()
    )
    db.add(snapshot)


# -----------------------------
# REAL MOVEMENT DETECTION
# -----------------------------
def calculate_real_movement(db, anime_id: int, current_score: float):
    history = (
        db.query(AnimeTrendHistory)
        .filter(AnimeTrendHistory.anime_id == anime_id)
        .order_by(AnimeTrendHistory.created_at.desc())
        .limit(2)
        .all()
    )

    if len(history) < 2:
        return "stable"

    previous_score = history[1].trend_score
    diff = current_score - previous_score

    if diff >= 10:
        return "spiking"
    elif diff >= 3:
        return "rising"
    elif diff <= -10:
        return "cooling"
    else:
        return "stable"


# -----------------------------
# LABEL MAPPING
# -----------------------------
def get_spike_label(movement: str):
    if movement == "spiking":
        return "🚀 Breaking Out"
    if movement == "rising":
        return "📈 Gaining Momentum"
    if movement == "cooling":
        return "📉 Cooling Down"
    return "➖ Stable Interest"


# -----------------------------
# TREND LEVEL (VISUAL)
# -----------------------------
def trend_level(score: float):
    if score >= 120:
        return "🔥 Hot"
    if score >= 80:
        return "📈 Rising"
    return "🟡 Stable"


# -----------------------------
# INSIGHT BUILDER
# -----------------------------
def build_insight(anime: Anime):
    parts = []

    if anime.score and anime.score >= 8:
        parts.append("Highly rated by community")

    if anime.poster_url:
        parts.append("Has official visuals")

    if anime.status == "upcoming":
        parts.append("Upcoming release generating hype")

    if anime.genres:
        if "Action" in anime.genres:
            parts.append("Action genre momentum")
        if "Fantasy" in anime.genres:
            parts.append("Fantasy audience interest")

    if not parts:
        parts.append("Standard tracking entry")

    return " • ".join(parts)


# -----------------------------
# MAIN ENDPOINT
# -----------------------------
@router.get("/")
def trending_anime():
    db = SessionLocal()

    try:
        anime_list = db.query(Anime).all()

        results = []

        for a in anime_list:
            score = calculate_trend_score(a)

            # Save snapshot (IMPORTANT: keeps history alive)
            save_trend_snapshot(db, a.id, score)

            # REAL movement based on history
            movement = calculate_real_movement(db, a.id, score)

            results.append({
                "id": a.id,
                "title": a.title,
                "poster_url": a.poster_url,
                "score": a.score,
                "trend_score": score,
                "status": a.status,

                "trend_level": trend_level(score),
                "movement": movement,
                "spike_label": get_spike_label(movement),
                "insight": build_insight(a),
            })

        results.sort(key=lambda x: x["trend_score"], reverse=True)

        return results[:10]

    finally:
        db.close()