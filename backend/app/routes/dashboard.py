from fastapi import APIRouter
from app.database.connection import SessionLocal
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/")
def dashboard():
    db = SessionLocal()

    try:
        service = DashboardService(db)

        return {
            "trending": service.trending(),
            "highest_rated": service.highest_rated(),
            "latest_news": service.latest_news(),
            "upcoming": service.upcoming(),
            "maple_picks": service.maple_picks(),
        }

    finally:
        db.close()
