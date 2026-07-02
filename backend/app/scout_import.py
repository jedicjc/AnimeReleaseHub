import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from app.database.connection import SessionLocal
from app.database.models import Anime, NewsArticle
from app.scout.config import JIKAN_DELAY, REQUEST_TIMEOUT, SCOUT_LIMIT
from app.scout.sources import HEADERS, MAL_NEWS_URL


JIKAN_API_URL = "https://api.jikan.moe/v4/anime"


def classify_article(headline: str) -> str:
    text = headline.lower()

    if "second season" in text or "season 2" in text:
        return "sequel"
    if "tv anime adaptation" in text or "gets tv anime" in text:
        return "new_adaptation"
    if "trailer" in text or "promo" in text or "teaser" in text:
        return "trailer"
    if "cast" in text:
        return "cast_update"
    if "staff" in text:
        return "staff_update"
    if "dub" in text or "english dub" in text:
        return "dub_update"
    if "delayed" in text:
        return "delay"

    return "general"


def extract_anime_title(headline: str) -> Optional[str]:
    quoted_match = re.search(r"'([^']+)'", headline)

    if quoted_match:
        return quoted_match.group(1).strip()

    known_titles = [
        "Cyberpunk: Edgerunners 2",
    ]

    for title in known_titles:
        if title.lower() in headline.lower():
            return title

    return None


def extract_release_info(headline: str):
    release_season = None
    release_year = None

    for season in ["Winter", "Spring", "Summer", "Fall"]:
        if season.lower() in headline.lower():
            release_season = season
            break

    year_match = re.search(r"\b(20\d{2})\b", headline)
    if year_match:
        release_year = int(year_match.group(1))

    return release_season, release_year


def fetch_jikan_metadata(title: str):
    try:
        response = requests.get(
            JIKAN_API_URL,
            params={"q": title, "limit": 1, "sfw": "true"},
            timeout=REQUEST_TIMEOUT,
            headers=HEADERS,
        )

        response.raise_for_status()
        payload = response.json()
        results = payload.get("data", [])

        if not results:
            return {}

        anime = results[0]

        images = anime.get("images", {})
        jpg = images.get("jpg", {})

        genres = ", ".join(
            genre.get("name", "")
            for genre in anime.get("genres", [])
            if genre.get("name")
        )

        return {
            "display_title": anime.get("title_english") or anime.get("title") or title,
            "poster_url": jpg.get("large_image_url") or jpg.get("image_url"),
            "synopsis": anime.get("synopsis"),
            "score": anime.get("score"),
            "genres": genres or None,
        }

    except Exception as error:
        print(f"Jikan lookup failed for {title}: {error}")
        return {}


def fetch_mal_articles(limit: int = 10):
    response = requests.get(
        MAL_NEWS_URL,
        timeout=REQUEST_TIMEOUT,
        headers=HEADERS,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    for link in soup.select("a"):
        title = link.get_text(strip=True)
        href = link.get("href")

        if not title or not href:
            continue

        if href.startswith("/"):
            href = "https://myanimelist.net" + href

        if (
            len(title) > 30
            and "${" not in title
            and "View all results" not in title
            and "myanimelist.net/news/" in href
        ):
            articles.append(
                {
                    "title": title,
                    "source": "MyAnimeList",
                    "url": href,
                    "category": classify_article(title),
                }
            )

        if len(articles) >= limit:
            break

    return articles


def upsert_news_article(db, article):
    pending = next(
        (
            item
            for item in db.new
            if isinstance(item, NewsArticle) and item.url == article["url"]
        ),
        None,
    )

    existing = (
        db.query(NewsArticle)
        .filter(NewsArticle.url == article["url"])
        .first()
    )

    if not existing and pending:
        existing = pending

    if existing:
        existing.title = article["title"]
        existing.category = article["category"]
        existing.source = article["source"]
        return "updated"

    db.add(
        NewsArticle(
            title=article["title"],
            source=article["source"],
            url=article["url"],
            category=article["category"],
            summary=None,
            processed=False,
        )
    )

    return "created"


def upsert_anime_from_article(db, article):
    extracted_title = extract_anime_title(article["title"])

    if not extracted_title:
        return "skipped"

    release_season, release_year = extract_release_info(article["title"])

    metadata = fetch_jikan_metadata(extracted_title)
    time.sleep(JIKAN_DELAY)

    anime_title = metadata.get("display_title") or extracted_title

    pending = next(
        (
            item
            for item in db.new
            if isinstance(item, Anime) and item.title == anime_title
        ),
        None,
    )

    existing = (
        db.query(Anime)
        .filter(Anime.source_url == article["url"])
        .first()
    )

    if not existing and pending:
        existing = pending

    if not existing:
        existing = (
            db.query(Anime)
            .filter(Anime.title == anime_title)
            .first()
        )

    if existing:
        existing.title = anime_title
        existing.release_season = release_season
        existing.release_year = release_year
        existing.source_url = existing.source_url or article["url"]

        if release_year:
            existing.status = "upcoming"

        if metadata.get("poster_url"):
            existing.poster_url = metadata["poster_url"]

        if metadata.get("synopsis"):
            existing.synopsis = metadata["synopsis"]

        if metadata.get("score") is not None:
            existing.score = metadata["score"]

        if metadata.get("genres"):
            existing.genres = metadata["genres"]

        return "updated"

    db.add(
        Anime(
            title=anime_title,
            status="upcoming" if release_year else "announced",
            release_season=release_season,
            release_year=release_year,
            source_url=article["url"],
            poster_url=metadata.get("poster_url"),
            synopsis=metadata.get("synopsis"),
            score=metadata.get("score"),
            genres=metadata.get("genres"),
            notes=f"Created automatically from headline: {article['title']}",
        )
    )

    return "created"


def save_articles():
    db = SessionLocal()

    stats = {
        "articles_created": 0,
        "articles_updated": 0,
        "anime_created": 0,
        "anime_updated": 0,
        "anime_skipped": 0,
    }

    try:
        articles = fetch_mal_articles(limit=SCOUT_LIMIT)

        for article in articles:
            article_status = upsert_news_article(db, article)

            if article_status == "created":
                stats["articles_created"] += 1
            else:
                stats["articles_updated"] += 1

            anime_status = upsert_anime_from_article(db, article)

            if anime_status == "created":
                stats["anime_created"] += 1
            elif anime_status == "updated":
                stats["anime_updated"] += 1
            else:
                stats["anime_skipped"] += 1

        db.commit()

        print("\nMaple Scout 2.0 Import Complete")
        print(f"Articles Created: {stats['articles_created']}")
        print(f"Articles Updated: {stats['articles_updated']}")
        print(f"Anime Created:    {stats['anime_created']}")
        print(f"Anime Updated:    {stats['anime_updated']}")
        print(f"Anime Skipped:    {stats['anime_skipped']}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    save_articles()
