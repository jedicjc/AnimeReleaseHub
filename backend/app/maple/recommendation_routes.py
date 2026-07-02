from fastapi import APIRouter
from app.maple.recommendations import get_similar_anime

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/{anime_id}")
def similar(anime_id: int):
    try:
        return get_similar_anime(anime_id)
    except Exception:
        return []
