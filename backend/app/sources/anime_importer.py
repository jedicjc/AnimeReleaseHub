from app.database.connection import SessionLocal
from app.database.models import Anime
from app.maple.scoring import calculate_maple_score
from app.sources.anilist_client import AniListClient
from app.sources.jikan_client import JikanClient


class AnimeImporter:
    def __init__(self, db, anilist_client=None, jikan_client=None):
        self.db = db
        self.anilist_client = anilist_client or AniListClient()
        self.jikan_client = jikan_client or JikanClient()

    def import_title(self, title: str, source_url: str | None = None, notes: str | None = None):
        catalog_data = self.anilist_client.search_anime(title)
        if not catalog_data:
            return None

        enrichment = self.jikan_client.enrich_title(
            catalog_data.get("display_title") or title
        )
        return self.upsert_anime(
            title=title,
            catalog_data=catalog_data,
            enrichment=enrichment,
            source_url=source_url,
            notes=notes,
        )

    def upsert_anime(
        self,
        title: str,
        catalog_data: dict,
        enrichment: dict | None = None,
        source_url: str | None = None,
        notes: str | None = None,
    ):
        enrichment = enrichment or {}
        display_title = (
            enrichment.get("display_title")
            or catalog_data.get("display_title")
            or title
        )

        anime = (
            self.db.query(Anime)
            .filter(Anime.title == display_title)
            .first()
        )

        if not anime and source_url:
            anime = (
                self.db.query(Anime)
                .filter(Anime.source_url == source_url)
                .first()
            )

        if not anime:
            anime = Anime(
                title=display_title,
                source_url=source_url,
                notes=notes,
            )
            self.db.add(anime)

        merged = {**catalog_data, **enrichment}

        anime.title = merged.get("display_title") or display_title
        anime.status = merged.get("status") or anime.status or "announced"
        anime.release_season = merged.get("release_season")
        anime.release_year = merged.get("release_year")
        anime.source_url = source_url or anime.source_url
        anime.poster_url = merged.get("poster_url")
        anime.synopsis = merged.get("synopsis")
        anime.score = merged.get("score")
        anime.genres = merged.get("genres")
        anime.japanese_title = merged.get("japanese_title")
        anime.anime_type = merged.get("anime_type")
        anime.episodes = merged.get("episodes")
        anime.rating = merged.get("rating")
        anime.studio = merged.get("studio")
        anime.trailer_url = merged.get("trailer_url")
        anime.members = merged.get("members")
        anime.favorites = merged.get("favorites")
        anime.rank = merged.get("rank")
        anime.popularity = merged.get("popularity")
        anime.aired_from = merged.get("aired_from")
        anime.aired_to = merged.get("aired_to")
        anime.notes = notes or anime.notes

        self.db.flush()
        anime.maple_score = calculate_maple_score(anime)
        return anime


def join_names(items):
    if not items:
        return ""

    return ", ".join(
        item.get("name", "")
        for item in items
        if item.get("name")
    )


def upsert_anime(db, item):
    title = item.get("title")

    if not title:
        return None

    source_url = item.get("url")
    anime = db.query(Anime).filter(Anime.title == title).first()

    if not anime and source_url:
        anime = db.query(Anime).filter(Anime.source_url == source_url).first()

    if not anime:
        anime = Anime(title=title, source_url=source_url)
        db.add(anime)

    images = item.get("images") or {}
    jpg = images.get("jpg") or {}
    trailer = item.get("trailer") or {}

    anime.title = title
    anime.japanese_title = item.get("title_japanese")
    anime.anime_type = item.get("type")
    anime.episodes = item.get("episodes")
    anime.status = (item.get("status") or "").lower() or anime.status or "announced"
    anime.release_season = item.get("season")
    anime.release_year = item.get("year")
    anime.synopsis = item.get("synopsis")
    anime.rating = item.get("rating")
    anime.score = item.get("score")
    anime.rank = item.get("rank")
    anime.popularity = item.get("popularity")
    anime.members = item.get("members")
    anime.favorites = item.get("favorites")
    anime.genres = join_names(item.get("genres")) or anime.genres
    anime.studio = join_names(item.get("studios")) or anime.studio
    anime.poster_url = jpg.get("large_image_url") or jpg.get("image_url")
    anime.trailer_url = trailer.get("url")
    anime.source_url = source_url or anime.source_url

    db.flush()
    anime.maple_score = calculate_maple_score(anime)
    return anime


def import_top_anime(pages=3):
    client = JikanClient()
    db = SessionLocal()

    imported = 0

    try:
        for page in range(1, pages + 1):
            payload = client.top_anime(page=page)

            for item in payload.get("data", []):
                anime = upsert_anime(db, item)

                if anime:
                    imported += 1

            db.commit()

        return imported

    finally:
        db.close()


def import_current_season(pages=2):
    client = JikanClient()
    db = SessionLocal()

    imported = 0

    try:
        for page in range(1, pages + 1):
            payload = client.current_season(page=page)

            for item in payload.get("data", []):
                anime = upsert_anime(db, item)

                if anime:
                    imported += 1

            db.commit()

        return imported

    finally:
        db.close()
