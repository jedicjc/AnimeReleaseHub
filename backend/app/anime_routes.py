from fastapi import APIRouter
from app.database.connection import SessionLocal
from app.database.models import Anime

router = APIRouter(prefix="/anime", tags=["Anime"])


@router.get("/")
def list_anime():
    db = SessionLocal()

    try:
        anime = db.query(Anime).all()
        return anime
    finally:
        db.close()