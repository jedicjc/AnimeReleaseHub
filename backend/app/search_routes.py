from fastapi import APIRouter, Query
from app.database.connection import SessionLocal
from app.database.models import Anime, NewsArticle

router = APIRouter(prefix="/search", tags=["Search"])


def score_match(text: str, query: str):
    text = (text or "").lower()
    query = query.lower()

    if text == query:
        return 100

    if text.startswith(query):
        return 80

    if query in text:
        return 50

    return 0


@router.get("/")
def search(query: str = Query(..., min_length=2)):
    db = SessionLocal()

    try:
        anime_rows = db.query(Anime).all()
        news_rows = db.query(NewsArticle).all()

        ranked_anime = []
        ranked_news = []

        for a in anime_rows:
            score = score_match(a.title, query)
            score = max(score, score_match(getattr(a, "title_english", None), query))
            score = max(score, score_match(a.japanese_title, query))

            if a.synopsis:
                score += score_match(a.synopsis, query) * 0.3

            if a.genres:
                score += score_match(a.genres, query) * 0.2

            if score > 0:
                ranked_anime.append({
                    "id": a.id,
                    "title": a.title,
                    "title_english": getattr(a, "title_english", None),
                    "poster_url": a.poster_url,
                    "score": score
                })

        for n in news_rows:
            score = score_match(n.title, query)

            if score > 0:
                ranked_news.append({
                    "id": n.id,
                    "title": n.title,
                    "url": n.url,
                    "score": score
                })

        ranked_anime.sort(key=lambda x: x["score"], reverse=True)
        ranked_news.sort(key=lambda x: x["score"], reverse=True)

        return {
            "query": query,
            "anime": ranked_anime[:8],
            "news": ranked_news[:8]
        }

    finally:
        db.close()
