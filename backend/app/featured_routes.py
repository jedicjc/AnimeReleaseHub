from fastapi import APIRouter
from sqlalchemy import desc, nullslast

from app.database.connection import SessionLocal
from app.database.models import Anime

router = APIRouter(prefix="/featured", tags=["Featured"])


@router.get("/")
def featured_anime():
    db = SessionLocal()

    try:
        anime = (
            db.query(Anime)
            .filter(
                Anime.poster_url.is_not(None)
            )
            .order_by(
                # Primary signal: quality
                nullslast(desc(Anime.score)),

                # Secondary: most recent meaningful release info
                nullslast(desc(Anime.release_year)),

                # Tertiary: newest added
                desc(Anime.created_at),
            )
            .first()
        )

        return anime

    finally:
        db.close()