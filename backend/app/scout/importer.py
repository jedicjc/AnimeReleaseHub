from app.database.connection import SessionLocal
from app.database.models import Anime, NewsArticle
from app.maple.scoring import calculate_maple_score
from app.scout.intelligence import ScoutIntelligence
from app.scout.matcher import ScoutMatcher
from app.scout.normalizer import ScoutNormalizer
from app.scout.providers.crunchyroll import CrunchyrollProvider
from app.scout.providers.hidive import HidiveProvider
from app.scout.providers.jikan import JikanProvider


class ScoutImporter:
    def __init__(self):
        self.intelligence = ScoutIntelligence()
        self.normalizer = ScoutNormalizer()

    def upsert_anime(self, db, data):
        mal_id = data.get("mal_id")
        title = data.get("title")

        if not title:
            return None

        anime = None

        if mal_id and hasattr(Anime, "mal_id"):
            anime = db.query(Anime).filter(Anime.mal_id == mal_id).first()

        if not anime:
            anime = db.query(Anime).filter(Anime.title == title).first()

        if not anime:
            anime = Anime(title=title)
            db.add(anime)

        for field, value in data.items():
            if field == "title_japanese" and hasattr(anime, "japanese_title"):
                setattr(anime, "japanese_title", value)
                continue

            if field == "type" and hasattr(anime, "anime_type"):
                setattr(anime, "anime_type", value)
                continue

            if field == "season" and hasattr(anime, "release_season"):
                setattr(anime, "release_season", value)
                continue

            if field == "year" and hasattr(anime, "release_year"):
                setattr(anime, "release_year", value)
                continue

            if field == "studios" and hasattr(anime, "studio"):
                setattr(anime, "studio", value)
                continue

            if field == "image_url" and hasattr(anime, "poster_url"):
                setattr(anime, "poster_url", value)
                continue

            if hasattr(anime, field):
                setattr(anime, field, value)

        if hasattr(anime, "status") and anime.status:
            anime.status = anime.status.lower()

        db.flush()
        anime.maple_score = calculate_maple_score(anime)
        return anime

    def save_news_article(self, db, data):
        url = data.get("url")

        if not url:
            return None

        matcher = ScoutMatcher(db)

        matched_anime = matcher.find_anime_for_news(
            title=data.get("title", ""),
            summary=data.get("summary", ""),
        )

        existing = db.query(NewsArticle).filter(NewsArticle.url == url).first()

        if existing:
            for field, value in data.items():
                if hasattr(existing, field) and value is not None:
                    setattr(existing, field, value)

            if matched_anime and hasattr(existing, "anime_id") and not existing.anime_id:
                existing.anime_id = matched_anime.id

            return existing

        article = NewsArticle()

        for field, value in data.items():
            if hasattr(article, field):
                setattr(article, field, value)

        if matched_anime and hasattr(article, "anime_id"):
            article.anime_id = matched_anime.id

        intel = self.intelligence.analyze_article(article)

        article.intelligence_category = intel.get("category")
        article.intelligence_importance = intel.get("importance")
        article.intelligence_event = intel.get("event")
        article.intelligence_anime = intel.get("anime")
        article.intelligence_summary = intel.get("summary")

        db.add(article)
        return article

    def import_jikan_top(self, pages=3, limit=25):
        provider = JikanProvider()
        db = SessionLocal()
        imported = 0

        try:
            for page in range(1, pages + 1):
                items = provider.fetch_top_anime(page=page, limit=limit)

                for item in items:
                    data = self.normalizer.normalize_jikan_anime(item)
                    anime = self.upsert_anime(db, data)

                    if anime:
                        imported += 1

                db.commit()

            return imported

        finally:
            db.close()

    def import_jikan_season(self, pages=2, limit=25):
        provider = JikanProvider()
        db = SessionLocal()
        imported = 0

        try:
            for page in range(1, pages + 1):
                items = provider.fetch_current_season(page=page, limit=limit)

                for item in items:
                    data = self.normalizer.normalize_jikan_anime(item)
                    anime = self.upsert_anime(db, data)

                    if anime:
                        imported += 1

                db.commit()

            return imported

        finally:
            db.close()

    def import_crunchyroll_news(self, limit=25):
        provider = CrunchyrollProvider()
        db = SessionLocal()
        inserted = 0
        duplicates = 0

        try:
            try:
                result = provider.fetch_news(limit=limit)
            except Exception as error:
                return {
                    "provider": "crunchyroll",
                    "fetched": 0,
                    "inserted": 0,
                    "duplicates": 0,
                    "error": repr(error),
                }

            items = result.get("items", [])
            diagnostics = result.get("diagnostics", {})

            for item in items:
                data = self.normalizer.normalize_news(item)
                existing = (
                    db.query(NewsArticle)
                    .filter(NewsArticle.url == data.get("url"))
                    .first()
                )
                article = self.save_news_article(db, data)

                if article and not existing:
                    inserted += 1
                else:
                    duplicates += 1

            db.commit()
            return {
                "provider": "crunchyroll",
                "fetched": len(items),
                "inserted": inserted,
                "duplicates": duplicates,
                "diagnostics": diagnostics,
            }

        finally:
            db.close()

    def import_hidive_news(self, limit=25):
        provider = HidiveProvider()
        db = SessionLocal()
        inserted = 0
        duplicates = 0

        try:
            try:
                result = provider.fetch_news(limit=limit)
            except Exception as error:
                return {
                    "provider": "hidive",
                    "fetched": 0,
                    "inserted": 0,
                    "duplicates": 0,
                    "error": repr(error),
                }

            items = result.get("items", [])
            diagnostics = result.get("diagnostics", {})

            for item in items:
                data = self.normalizer.normalize_news(item)
                existing = (
                    db.query(NewsArticle)
                    .filter(NewsArticle.url == data.get("url"))
                    .first()
                )
                article = self.save_news_article(db, data)

                if article and not existing:
                    inserted += 1
                else:
                    duplicates += 1

            db.commit()
            return {
                "provider": "hidive",
                "fetched": len(items),
                "inserted": inserted,
                "duplicates": duplicates,
                "diagnostics": diagnostics,
            }

        finally:
            db.close()


def import_top_anime(pages=3, limit=25):
    return ScoutImporter().import_jikan_top(pages=pages, limit=limit)


def import_current_season(pages=2, limit=25):
    return ScoutImporter().import_jikan_season(pages=pages, limit=limit)


def import_crunchyroll_news(limit=25):
    return ScoutImporter().import_crunchyroll_news(limit=limit)


def import_hidive_news(limit=25):
    return ScoutImporter().import_hidive_news(limit=limit)
