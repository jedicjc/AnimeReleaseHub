from app.database.connection import SessionLocal
from app.database.models import Anime, NewsArticle
from app.maple.scoring import calculate_maple_score
from app.scout.article_classifier import (
    canonical_event_name,
    event_family_key,
    event_key,
    event_seasons,
)
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

    def get_db(self):
        return SessionLocal()

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

        if not anime and data.get("title_english"):
            anime = (
                db.query(Anime)
                .filter(Anime.title_english == data.get("title_english"))
                .first()
            )

        if not anime and data.get("title_japanese"):
            anime = (
                db.query(Anime)
                .filter(Anime.japanese_title == data.get("title_japanese"))
                .first()
            )

        if not anime:
            anime = Anime(title=title)
            db.add(anime)

        promoted_title = self.choose_display_title(
            db=db,
            anime=anime,
            current_title=getattr(anime, "title", None),
            incoming_title=title,
            title_english=data.get("title_english"),
        )

        if promoted_title:
            anime.title = promoted_title

        for field, value in data.items():
            if field == "title_english" and hasattr(anime, "title_english"):
                self.assign_if_present(anime, "title_english", value)
                continue

            if field == "title_japanese" and hasattr(anime, "japanese_title"):
                self.assign_if_present(anime, "japanese_title", value)
                continue

            if field == "type" and hasattr(anime, "anime_type"):
                self.assign_if_present(anime, "anime_type", value)
                continue

            if field == "season" and hasattr(anime, "release_season"):
                self.assign_if_present(anime, "release_season", value)
                continue

            if field == "year" and hasattr(anime, "release_year"):
                self.assign_if_present(anime, "release_year", value)
                continue

            if field == "studios" and hasattr(anime, "studio"):
                self.assign_if_present(anime, "studio", value)
                continue

            if field == "image_url" and hasattr(anime, "poster_url"):
                self.assign_if_present(anime, "poster_url", value)
                continue

            if hasattr(anime, field):
                self.assign_if_present(anime, field, value)

        if hasattr(anime, "status") and anime.status:
            anime.status = anime.status.lower()

        db.flush()
        anime.maple_score = calculate_maple_score(anime)
        return anime

    def assign_if_present(self, model, field: str, value):
        if value is None:
            return

        if isinstance(value, str) and not value.strip():
            return

        setattr(model, field, value)

    def choose_display_title(
        self,
        db,
        anime,
        current_title: str | None,
        incoming_title: str | None,
        title_english: str | None,
    ) -> str | None:
        if not current_title:
            return title_english or incoming_title

        if not title_english or current_title == title_english:
            return current_title

        if current_title in {
            incoming_title,
            getattr(anime, "japanese_title", None),
        }:
            title_taken = (
                db.query(Anime)
                .filter(Anime.title == title_english, Anime.id != anime.id)
                .first()
            )

            if not title_taken:
                return title_english

        return current_title

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

            if existing.intelligence_category:
                existing.category = existing.intelligence_category
                return existing

            intel = self.intelligence.analyze_article(
                existing,
                matched_anime=matched_anime,
            )
            self.apply_article_intelligence(
                db,
                existing,
                intel,
                matched_anime=matched_anime,
            )
            return existing

        article = NewsArticle()

        for field, value in data.items():
            if hasattr(article, field):
                setattr(article, field, value)

        if matched_anime and hasattr(article, "anime_id"):
            article.anime_id = matched_anime.id

        intel = self.intelligence.analyze_article(
            article,
            matched_anime=matched_anime,
        )

        self.apply_article_intelligence(
            db,
            article,
            intel,
            matched_anime=matched_anime,
        )

        db.add(article)
        return article

    def apply_article_intelligence(self, db, article, intel, matched_anime=None):
        anime_title = (
            intel.get("anime")
            or (getattr(matched_anime, "title", None) if matched_anime else None)
        )
        event = canonical_event_name(
            anime_title=anime_title,
            category=intel.get("category"),
            title=article.title,
            summary=article.summary,
            fallback_event=intel.get("event"),
        )
        event = self.find_existing_event(db, event) or event

        article.category = intel.get("category")
        article.intelligence_category = intel.get("category")
        article.intelligence_importance = intel.get("importance")
        article.intelligence_confidence = intel.get("confidence")
        article.intelligence_event = event
        article.intelligence_anime = anime_title
        article.intelligence_summary = intel.get("summary")
        article.intelligence_tags = intel.get("tags")

    def find_existing_event(self, db, event_name):
        key = event_key(event_name)
        family_key = event_family_key(event_name)
        seasons = event_seasons(event_name)

        if not key:
            return None

        pending = [
            item
            for item in db.new
            if isinstance(item, NewsArticle)
            and item.intelligence_event
        ]
        saved = (
            db.query(NewsArticle)
            .filter(NewsArticle.intelligence_event.isnot(None))
            .all()
        )

        for article in pending + saved:
            candidate = article.intelligence_event

            if event_key(candidate) == key:
                return candidate

            candidate_seasons = event_seasons(candidate)
            both_have_different_seasons = (
                seasons
                and candidate_seasons
                and seasons != candidate_seasons
            )

            if (
                family_key
                and event_family_key(candidate) == family_key
                and not both_have_different_seasons
            ):
                return candidate

        return None

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
