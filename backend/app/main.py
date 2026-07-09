import asyncio
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(override=False)

from app.database.connection import (
    engine,
    ensure_anime_metadata_columns,
    ensure_news_article_columns,
    ensure_news_intelligence_columns,
)
from app.database.models import Base

from app.news_routes import router as news_router
from app.anime_routes import router as anime_router
from app.routes.dashboard import router as dashboard_router
from app.search_routes import router as search_router
from app.featured_routes import router as featured_router
from app.import_routes import router as import_router
from app.trending_routes import router as trending_router
from app.maple.routes import router as maple_router
from app.maple.recommendation_routes import router as rec_router
from app.maple.dashboard_routes import router as maple_dashboard_router
from app.maple.explanation_routes import router as explain_router
from app.maple.personalization_routes import router as personal_router
from app.maple.chat_routes import router as chat_router
from app.maple.trend_routes import router as trending_router
from app.event_routes import router as event_router
from app.scout.scheduler import ScoutScheduler
from app.scout_routes import router as scout_router

# Create DB tables
Base.metadata.create_all(bind=engine)
ensure_anime_metadata_columns()
ensure_news_article_columns()
ensure_news_intelligence_columns()


@asynccontextmanager
async def lifespan(app):
    scheduler = ScoutScheduler()

    asyncio.create_task(
        scheduler.run_forever()
    )

    yield


app = FastAPI(title="AnimeReleaseHub API", lifespan=lifespan)


def get_cors_origins():
    configured_origins = os.getenv("CORS_ORIGINS")

    if configured_origins:
        return [
            origin.strip()
            for origin in configured_origins.split(",")
            if origin.strip()
        ]

    return [
        "https://your-vercel-app.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
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
app.include_router(import_router)
app.include_router(trending_router)
app.include_router(maple_router)
app.include_router(rec_router)
app.include_router(maple_dashboard_router)
app.include_router(explain_router)
app.include_router(personal_router)
app.include_router(chat_router)
app.include_router(trending_router)
app.include_router(event_router)
app.include_router(scout_router)

@app.get("/")
def root():
    return {"status": "AnimeReleaseHub API running 🍁"}
