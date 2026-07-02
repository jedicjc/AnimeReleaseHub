from fastapi import APIRouter
from app.database.connection import SessionLocal
from app.database.models import NewsArticle

router = APIRouter(prefix="/news", tags=["News"])


@router.get("/")
def list_news():
    db = SessionLocal()

    try:
        articles = db.query(NewsArticle).order_by(NewsArticle.created_at.desc()).all()
        return articles
    finally:
        db.close()