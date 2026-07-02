import re

import requests
from bs4 import BeautifulSoup

from app.database.connection import SessionLocal
from app.database.models import Anime, NewsArticle


def classify_article(headline: str):
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


def extract_anime_title(headline: str):
    quoted_match = re.search(r"'([^']+)'", headline)

    if quoted_match:
        return quoted_match.group(1)

    if "Cyberpunk: Edgerunners 2" in headline:
        return "Cyberpunk: Edgerunners 2"

    return None


def extract_release_info(headline: str):
    release_season = None
    release_year = None

    seasons = ["Winter", "Spring", "Summer", "Fall"]

    for season in seasons:
        if season.lower() in headline.lower():
            release_season = season
            break

    year_match = re.search(r"\b(20\d{2})\b", headline)
    if year_match:
        release_year = int(year_match.group(1))

    return release_season, release_year


def fetch_mal_articles():
    url = "https://myanimelist.net/news"

    response = requests.get(
        url,
        timeout=15,
        headers={"User-Agent": "AnimeReleaseHub MapleOS/0.1"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    articles = []

    for link in soup.select("a"):
        title = link.get_text(strip=True)
        href = link.get("href")

        if not href:
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

        if len(articles) >= 10:
            break

    return articles


def save_articles():
    db = SessionLocal()

    saved_articles = 0
    skipped_articles = 0
    created_anime = 0
    updated_anime = 0

    try:
        articles = fetch_mal_articles()

        for article in articles:
            existing_article = (
                db.query(NewsArticle)
                .filter(NewsArticle.url == article["url"])
                .first()
            )

            if existing_article:
                existing_article.category = article["category"]
                skipped_articles += 1
            else:
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
                saved_articles += 1

            anime_title = extract_anime_title(article["title"])

            if not anime_title:
                continue

            release_season, release_year = extract_release_info(article["title"])

            existing_anime = (
                db.query(Anime)
                .filter(Anime.title == anime_title)
                .first()
            )

            if existing_anime:
                existing_anime.release_season = release_season
                existing_anime.release_year = release_year

                if release_year:
                    existing_anime.status = "upcoming"

                updated_anime += 1
                continue

            db.add(
                Anime(
                    title=anime_title,
                    status="upcoming" if release_year else "announced",
                    release_season=release_season,
                    release_year=release_year,
                    source_url=article["url"],
                    notes=f"Created automatically from headline: {article['title']}",
                )
            )

            created_anime += 1

        db.commit()

        print("\n🍁 Maple Scout Import Complete")
        print(f"New Articles:      {saved_articles}")
        print(f"Skipped Articles:  {skipped_articles}")
        print(f"New Anime:         {created_anime}")
        print(f"Updated Anime:     {updated_anime}")

    finally:
        db.close()


if __name__ == "__main__":
    save_articles()