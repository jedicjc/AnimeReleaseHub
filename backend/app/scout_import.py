import requests
from bs4 import BeautifulSoup

from app.database.connection import SessionLocal
from app.database.models import NewsArticle


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

    saved = 0
    skipped = 0

    try:
        articles = fetch_mal_articles()

        for article in articles:
            existing = (
                db.query(NewsArticle)
                .filter(NewsArticle.url == article["url"])
                .first()
            )

            if existing:
                skipped += 1
                continue

            db_article = NewsArticle(
                title=article["title"],
                source=article["source"],
                url=article["url"],
                summary=None,
                processed=False,
            )

            db.add(db_article)
            saved += 1

        db.commit()

        print("🍁 Maple Scout import complete.")
        print(f"Saved new articles: {saved}")
        print(f"Skipped duplicates: {skipped}")

    finally:
        db.close()


if __name__ == "__main__":
    save_articles()