from fastapi import FastAPI
from app.database.connection import test_database_connection
from app.database.models import Base
from app.database.connection import engine

app = FastAPI(
    title="AnimeReleaseHub API",
    version="0.1.0-alpha",
    description="Backend API for AnimeReleaseHub, powered by MapleOS.",
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