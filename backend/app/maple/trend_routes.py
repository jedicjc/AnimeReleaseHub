from fastapi import APIRouter
from app.maple.trends import get_trending_anime

router = APIRouter(prefix="/trending", tags=["Trending"])


@router.get("/")
def trending():
    try:
        return get_trending_anime()
    except Exception:
        return []
