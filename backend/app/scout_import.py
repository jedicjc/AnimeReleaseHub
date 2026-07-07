import re
from typing import Optional

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(override=False)

from app.database.connection import SessionLocal
from app.database.models import Anime, NewsArticle
from app.scout.config import REQUEST_TIMEOUT, SCOUT_LIMIT
from app.scout.importer import ScoutImporter
from app.scout.sources import HEADERS, MAL_NEWS_URL
from app.maple.scoring import calculate_maple_score
from app.maple.trends import calculate_trend_score
from app.scout.article_classifier import classify_article as scout_classify_article
from app.sources.anime_importer import AnimeImporter

def classify_article(headline: str) -> str:
    return scout_classify_article(headline).value


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

def attach_article_to_anime(db, article_url: str, anime_id: int):
    article = (
        db.query(NewsArticle)
        .filter(NewsArticle.url == article_url)
        .first()
    )

    if article:
        article.anime_id = anime_id


def upsert_anime_from_article(db, article):
    extracted_title = extract_anime_title(article["title"])

    if not extracted_title:
        return "skipped"

    release_season, release_year = extract_release_info(article["title"])
    importer = AnimeImporter(db)
    existing = (
        db.query(Anime)
        .filter(Anime.source_url == article["url"])
        .first()
    )

    anime = importer.import_title(
        extracted_title,
        source_url=article["url"],
        notes=f"Created automatically from headline: {article['title']}",
    )

    if not anime:
        return "skipped"

    if release_season and not anime.release_season:
        anime.release_season = release_season

    if release_year and not anime.release_year:
        anime.release_year = release_year

    if release_year and anime.status in {None, "", "announced"}:
        anime.status = "upcoming"

    anime.trend_score = calculate_trend_score(article["category"], anime.score)
    anime.maple_score = calculate_maple_score(anime)
    attach_article_to_anime(db, article["url"], anime.id)

    return "updated" if existing else "created"


def refresh_incomplete_anime(db):
    importer = AnimeImporter(db)
    repaired = 0

    anime_rows = db.query(Anime).all()

    for anime in anime_rows:
        needs_repair = any(
            [
                not anime.poster_url,
                not anime.synopsis,
                anime.score is None,
                not getattr(anime, "title_english", None),
                not anime.japanese_title,
                not anime.studio,
                not anime.anime_type,
                anime.episodes is None,
                not anime.rating,
                anime.members is None,
                anime.favorites is None,
                anime.popularity is None,
                anime.rank is None,
            ]
        )

        if not needs_repair:
            continue

        search_title = getattr(anime, "title_english", None) or anime.title or anime.japanese_title

        if not search_title:
            continue

        repaired_anime = importer.import_title(
            search_title,
            source_url=anime.source_url,
            notes=anime.notes,
        )

        if repaired_anime:
            repaired += 1

    return repaired


def save_articles():
    db = SessionLocal()
    scout = ScoutImporter()

    stats = {
        "articles_created": 0,
        "articles_updated": 0,
        "anime_created": 0,
        "anime_updated": 0,
        "anime_skipped": 0,
        "anime_repaired": 0,
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

        stats["anime_repaired"] = refresh_incomplete_anime(db)

        db.commit()

        crunchyroll_result = scout.import_crunchyroll_news(limit=SCOUT_LIMIT)
        hidive_result = scout.import_hidive_news(limit=SCOUT_LIMIT)

        print("\nMaple Scout 2.0 Import Complete")
        print(f"Articles Created: {stats['articles_created']}")
        print(f"Articles Updated: {stats['articles_updated']}")
        print(f"Anime Created:    {stats['anime_created']}")
        print(f"Anime Updated:    {stats['anime_updated']}")
        print(f"Anime Skipped:    {stats['anime_skipped']}")
        print(f"Anime Repaired:   {stats['anime_repaired']}")
        print(
            "Crunchyroll News: "
            f"{crunchyroll_result.get('inserted', 0)} inserted, "
            f"{crunchyroll_result.get('duplicates', 0)} duplicates"
        )
        print(
            "HIDIVE News:      "
            f"{hidive_result.get('inserted', 0)} inserted, "
            f"{hidive_result.get('duplicates', 0)} duplicates"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    save_articles()
