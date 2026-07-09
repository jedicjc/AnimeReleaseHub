from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.database.connection import SessionLocal
from app.database.models import Anime, NewsArticle
from app.maple.chat_engine import MapleChatEngine
from app.maple.comparison_engine import MapleComparisonEngine
from app.maple.insight_engine import MapleInsightEngine
from app.news_utils import is_valid_news_title
from app.scout.matcher import ScoutMatcher

router = APIRouter(prefix="/anime", tags=["Anime"])


class ChatMessage(BaseModel):
    role: str
    content: str


class AskMapleRequest(BaseModel):
    question: str
    history: List[ChatMessage] = Field(default_factory=list)
    summary: Optional[str] = None


@router.get("/")
def list_anime():
    db = SessionLocal()

    try:
        anime = (
            db.query(Anime)
            .order_by(Anime.trend_score.desc(), Anime.created_at.desc())
            .all()
        )
        return anime
    finally:
        db.close()


@router.get("/{anime_id}/news")
def get_anime_news(anime_id: int):
    db = SessionLocal()

    try:
        articles = (
            db.query(NewsArticle)
            .filter(NewsArticle.anime_id == anime_id)
            .order_by(NewsArticle.created_at.desc())
            .all()
        )
        articles = [
            article
            for article in articles
            if is_valid_news_title(getattr(article, "title", None))
        ]

        if articles:
            return articles

        anime = db.query(Anime).filter(Anime.id == anime_id).first()

        if not anime:
            raise HTTPException(status_code=404, detail="Anime not found")

        matcher = ScoutMatcher(db)
        fallback_titles = {
            title.strip().lower()
            for title in matcher.anime_titles(anime)
            if title and title.strip()
        }

        if fallback_titles:
            related_articles = []
            unmatched_articles = (
                db.query(NewsArticle)
                .filter(NewsArticle.anime_id.is_(None))
                .order_by(NewsArticle.created_at.desc())
                .all()
            )

            for article in unmatched_articles:
                article_text = f"{article.title or ''} {article.summary or ''}".lower()

                if any(title in article_text for title in fallback_titles):
                    if is_valid_news_title(getattr(article, "title", None)):
                        related_articles.append(article)

            if related_articles:
                return related_articles

        if not anime.source_url:
            return []

        articles = (
            db.query(NewsArticle)
            .filter(NewsArticle.url == anime.source_url)
            .order_by(NewsArticle.created_at.desc())
            .all()
        )
        return [
            article
            for article in articles
            if is_valid_news_title(getattr(article, "title", None))
        ]

    finally:
        db.close()


@router.get("/{anime_id}/insight")
def get_anime_insight(anime_id: int):
    db = SessionLocal()

    try:
        anime = db.query(Anime).filter(Anime.id == anime_id).first()

        if not anime:
            return {"error": "Anime not found"}

        news = (
            db.query(NewsArticle)
            .filter(NewsArticle.anime_id == anime_id)
            .order_by(NewsArticle.created_at.desc())
            .limit(5)
            .all()
        )
        news = [
            article
            for article in news
            if is_valid_news_title(getattr(article, "title", None))
        ]

        engine = MapleInsightEngine(anime=anime, news=news)

        return {
            "anime_id": anime.id,
            "title": anime.title,
            "summary": engine.anime_summary(),
            "score_explanation": engine.score_explanation(),
            "score_breakdown": engine.score_breakdown(),
        }

    finally:
        db.close()


@router.post("/{anime_id}/ask")
def ask_maple(anime_id: int, request: AskMapleRequest):
    db = SessionLocal()

    try:
        anime = db.query(Anime).filter(Anime.id == anime_id).first()

        if not anime:
            raise HTTPException(status_code=404, detail="Anime not found")

        news = (
            db.query(NewsArticle)
            .filter(NewsArticle.anime_id == anime_id)
            .order_by(NewsArticle.created_at.desc())
            .limit(5)
            .all()
        )
        news = [
            article
            for article in news
            if is_valid_news_title(getattr(article, "title", None))
        ]

        comparison_engine = MapleComparisonEngine(db)
        engine = MapleChatEngine(
            anime=anime,
            news=news,
            history=request.history,
            summary=request.summary,
            comparison_engine=comparison_engine,
        )

        return {
            "answer": engine.answer(request.question),
        }

    finally:
        db.close()


@router.get("/{anime_id}")
def get_anime(anime_id: int):
    db = SessionLocal()

    try:
        anime = db.query(Anime).filter(Anime.id == anime_id).first()

        if not anime:
            raise HTTPException(status_code=404, detail="Anime not found")

        return anime
    finally:
        db.close()
