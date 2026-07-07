from fastapi import APIRouter

from app.scout.provider_registry import provider_health


router = APIRouter(
    prefix="/scout",
    tags=["Scout"],
)


@router.get("/status")
def scout_status():
    return provider_health()
