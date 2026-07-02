import re

import requests
from bs4 import BeautifulSoup

from app.database.connection import SessionLocal
from app.database.models import Anime, NewsArticle


def extract_anime_title(headline: str):
    quoted_match = re.search(r"'([^']+)'", headline)

    if quoted_match:
        return quoted_match.group(1)

    if "Cyberpunk: Edgerunners 2" in headline:
        return "Cyberpunk: Edgerunners 2"

    return None


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
    skipped_anime = 0

    try:
        articles = fetch_mal_articles()

        for article in articles:
            existing_article = (
                db.query(NewsArticle)
                .filter(NewsArticle.url == article["url"])
                .first()
            )

            if existing_article:
                skipped_articles += 1
            else:
                db_article = NewsArticle(
                    title=article["title"],
                    source=article["source"],
                    url=article["url"],
                    summary=None,
                    processed=False,
                )

                db.add(db_article)
                saved_articles += 1

            anime_title = extract_anime_title(article["title"])

            if not anime_title:
                continue

            existing_anime = (
                db.query(Anime)
                .filter(Anime.title == anime_title)
                .first()
            )

            if existing_anime:
                skipped_anime += 1
                continue

            db_anime = Anime(
                title=anime_title,
                status="announced",
                source_url=article["url"],
                notes=f"Created automatically from headline: {article['title']}",
            )

            db.add(db_anime)
            created_anime += 1

        db.commit()

        print("Maple Scout import complete.")
        print(f"Saved new articles: {saved_articles}")
        print(f"Skipped duplicate articles: {skipped_articles}")
        print(f"Created anime records: {created_anime}")
        print(f"Skipped duplicate anime: {skipped_anime}")

    finally:
        db.close()


if __name__ == "__main__":
    save_articles()