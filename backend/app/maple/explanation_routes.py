from fastapi import APIRouter

from app.maple.explanations import generate_explanation

router = APIRouter(prefix="/maple/explain", tags=["Explanations"])


@router.get("/{anime_id}")
def explain(anime_id: int):
    try:
        return generate_explanation(anime_id)
    except Exception:
        return None
