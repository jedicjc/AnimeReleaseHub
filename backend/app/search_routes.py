from fastapi import APIRouter, Query
from app.database.connection import SessionLocal
from app.database.models import NewsArticle

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
def search(query: str = Query(..., min_length=2)):
    db = SessionLocal()

    try:
        results = (
            db.query(NewsArticle)
            .filter(NewsArticle.title.ilike(f"%{query}%"))
            .order_by(NewsArticle.created_at.desc())
            .limit(10)
            .all()
        )

        return results
    finally:
        db.close()
