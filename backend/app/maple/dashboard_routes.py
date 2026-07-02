from fastapi import APIRouter

from app.maple.dashboard import get_dashboard_data

router = APIRouter(prefix="/maple/dashboard", tags=["Dashboard"])


@router.get("/")
def dashboard():
    try:
        return get_dashboard_data()
    except Exception:
        return {
            "summary": {
                "total_anime": 0,
                "average_trend": 0,
            },
            "rising": [],
            "stable": [],
            "cooling": [],
        }
