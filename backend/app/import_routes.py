from fastapi import APIRouter

from app.sources.anime_importer import import_current_season, import_top_anime


router = APIRouter(prefix="/imports", tags=["Imports"])


@router.post("/jikan/top")
def import_jikan_top(pages: int = 3):
    imported = import_top_anime(pages=pages)

    return {
        "source": "jikan_top",
        "imported": imported,
    }


@router.post("/jikan/season")
def import_jikan_season(pages: int = 2):
    imported = import_current_season(pages=pages)

    return {
        "source": "jikan_current_season",
        "imported": imported,
    }


@router.post("/news/crunchyroll")
def import_crunchyroll(limit: int = 25):
    from app.sources.news_importer import import_crunchyroll_news

    imported = import_crunchyroll_news(limit=limit)

    return {
        "source": "crunchyroll_news",
        "imported": imported,
    }
