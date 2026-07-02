from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import engine
from app.database.models import Base

from app.news_routes import router as news_router
from app.anime_routes import router as anime_router
from app.dashboard_routes import router as dashboard_router
from app.search_routes import router as search_router
from app.featured_routes import router as featured_router
from app.trending_routes import router as trending_router

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AnimeReleaseHub API")


# CORS (frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
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


@app.get("/")
def root():
    return {"status": "AnimeReleaseHub API running 🍁"}