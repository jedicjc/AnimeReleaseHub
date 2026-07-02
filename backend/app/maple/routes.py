from fastapi import APIRouter
from app.database.connection import SessionLocal
from app.database.models import Anime

from app.maple.analyzer import (
    calculate_hype,
    get_audience_type,
    build_maple_insight
)

router = APIRouter(prefix="/maple", tags=["Maple"])


@router.get("/anime/{anime_id}")
def get_maple_analysis(anime_id: int):
    db = SessionLocal()

    try:
        anime = db.query(Anime).filter(Anime.id == anime_id).first()

        if not anime:
            return {"error": "Anime not found"}

        hype = calculate_hype(anime)

        return {
            "id": anime.id,
            "title": anime.title,
            "hype_score": hype,
            "audience": get_audience_type(anime),
            "insight": build_maple_insight(anime),
        }

    finally:
        db.close()