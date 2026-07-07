from fastapi import APIRouter

from app.scout.importer import ScoutImporter
from app.scout.provider_registry import provider_health
from app.scout.scout_engine import ScoutEngine


router = APIRouter(prefix="/imports", tags=["Scout Imports"])
scout = ScoutImporter()
engine = ScoutEngine()


@router.post("/jikan/top")
def import_jikan_top(pages: int = 3, limit: int = 25):
    imported = scout.import_jikan_top(
        pages=pages,
        limit=limit,
    )

    return {
        "provider": "jikan",
        "type": "top",
        "imported": imported,
    }


@router.post("/jikan/season")
def import_jikan_season(pages: int = 2, limit: int = 25):
    imported = scout.import_jikan_season(
        pages=pages,
        limit=limit,
    )

    return {
        "provider": "jikan",
        "type": "season",
        "imported": imported,
    }


@router.post("/crunchyroll")
def import_crunchyroll(limit: int = 25):
    return scout.import_crunchyroll_news(limit=limit)


@router.post("/hidive")
def import_hidive(limit: int = 25):
    return scout.import_hidive_news(limit=limit)


@router.post("/run")
def run_scout():
    return engine.run()


@router.get("/status")
def scout_status():
    return provider_health()
