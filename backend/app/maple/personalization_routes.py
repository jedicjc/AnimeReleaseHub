from fastapi import APIRouter, Query

from app.maple.personalization import get_personalized_recommendations

router = APIRouter(prefix="/maple/personal", tags=["Personalization"])


@router.get("/")
def personal_recommendations(genres: str = Query(...)):
    try:
        genre_list = genres.split(",")

        return get_personalized_recommendations(genre_list)
    except Exception:
        return []
