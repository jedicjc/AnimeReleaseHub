from fastapi import FastAPI
from app.anime_routes import router as anime_router
from app.database.connection import test_database_connection
from app.database.models import Base
from app.database.connection import engine
from app.news_routes import router as news_router
from app.dashboard_routes import router as dashboard_router
from app.search_routes import router as search_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AnimeReleaseHub API",
    version="0.1.0-alpha",
    description="Backend API for AnimeReleaseHub, powered by MapleOS.",
)

app.include_router(anime_router)
app.include_router(news_router)
app.include_router(dashboard_router)
app.include_router(search_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "project": "AnimeReleaseHub",
        "powered_by": "MapleOS",
        "status": "online",
        "message": "🍁 Maple says the API is running.",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "anime-release-hub-api",
    }


@app.get("/database/health")
def database_health_check():
    connected = test_database_connection()

    return {
        "database": "postgresql",
        "connected": connected,
        "message": "🍁 Maple connected to the database.",
    }