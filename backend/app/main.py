import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(override=True)

from app.database.connection import engine
from app.database.models import Base

from app.news_routes import router as news_router
from app.anime_routes import router as anime_router
from app.dashboard_routes import router as dashboard_router
from app.search_routes import router as search_router
from app.featured_routes import router as featured_router
from app.trending_routes import router as trending_router
from app.maple.routes import router as maple_router
from app.maple.recommendation_routes import router as rec_router
from app.maple.dashboard_routes import router as maple_dashboard_router
from app.maple.explanation_routes import router as explain_router
from app.maple.personalization_routes import router as personal_router
from app.maple.chat_routes import router as chat_router
from app.maple.trend_routes import router as trending_router

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AnimeReleaseHub API")


def get_cors_origins():
    configured_origins = os.getenv("CORS_ORIGINS")

    if configured_origins:
        return [
            origin.strip()
            for origin in configured_origins.split(",")
            if origin.strip()
        ]

    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://your-frontend.vercel.app",
    ]


# CORS (frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(news_router)
app.include_router(anime_router)
app.include_router(dashboard_router)
app.include_router(search_router)
app.include_router(featured_router)
app.include_router(trending_router)
app.include_router(maple_router)
app.include_router(rec_router)
app.include_router(maple_dashboard_router)
app.include_router(explain_router)
app.include_router(personal_router)
app.include_router(chat_router)
app.include_router(trending_router)

@app.get("/")
def root():
    return {"status": "AnimeReleaseHub API running 🍁"}
