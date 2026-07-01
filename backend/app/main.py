from fastapi import FastAPI

app = FastAPI(
    title="AnimeReleaseHub API",
    version="0.1.0-alpha",
    description="Backend API for AnimeReleaseHub, powered by MapleOS.",
)


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