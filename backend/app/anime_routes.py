from fastapi import APIRouter, HTTPException
from app.database.connection import SessionLocal
from app.database.models import Anime

router = APIRouter(prefix="/anime", tags=["Anime"])


@router.get("/")
def list_anime():
    db = SessionLocal()

    try:
        anime = (
            db.query(Anime)
            .order_by(Anime.trend_score.desc(), Anime.created_at.desc())
            .all()
        )
        return anime
    finally:
        db.close()


@router.get("/{anime_id}")
def get_anime(anime_id: int):
    db = SessionLocal()

    try:
        anime = db.query(Anime).filter(Anime.id == anime_id).first()

        if not anime:
            raise HTTPException(status_code=404, detail="Anime not found")

        return anime
    finally:
        db.close()
