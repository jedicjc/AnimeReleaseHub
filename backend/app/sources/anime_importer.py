from sqlalchemy import or_

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
        catalog_data = {}
        enrichment = {}

        try:
            catalog_data = self.anilist_client.search_anime(title) or {}
        except Exception as error:
            print(f"AniList lookup failed for {title}: {error}")

        jikan_title = catalog_data.get("display_title") or title

        try:
            enrichment = self.jikan_client.enrich_title(jikan_title) or {}
        except Exception as error:
            print(f"Jikan lookup failed for {title}: {error}")

        if not catalog_data and not enrichment:
            return None

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
        title_english = enrichment.get("title_english") or catalog_data.get("title_english")
        japanese_title = enrichment.get("japanese_title") or catalog_data.get("japanese_title")

        anime = (
            self.db.query(Anime)
            .filter(
                or_(
                    Anime.title == display_title,
                    Anime.title == title,
                    Anime.title_english == display_title,
                    Anime.title_english == title_english,
                    Anime.japanese_title == japanese_title,
                )
            )
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

        promoted_title = self.choose_display_title(
            anime=anime,
            searched_title=title,
            display_title=merged.get("display_title") or display_title,
            title_english=merged.get("title_english"),
        )

        if promoted_title:
            anime.title = promoted_title

        self.assign_if_present(anime, "mal_id", merged.get("mal_id"))
        self.assign_if_present(anime, "title_english", merged.get("title_english"))
        self.assign_if_present(
            anime,
            "status",
            (merged.get("status") or anime.status or "announced"),
        )
        self.assign_if_present(anime, "release_season", merged.get("release_season"))
        self.assign_if_present(anime, "release_year", merged.get("release_year"))
        anime.source_url = source_url or anime.source_url
        self.assign_if_present(anime, "poster_url", merged.get("poster_url"))
        self.assign_if_present(anime, "synopsis", merged.get("synopsis"))
        self.assign_if_present(anime, "score", merged.get("score"))
        self.assign_if_present(anime, "genres", merged.get("genres"))
        self.assign_if_present(anime, "japanese_title", merged.get("japanese_title"))
        self.assign_if_present(anime, "anime_type", merged.get("anime_type"))
        self.assign_if_present(anime, "episodes", merged.get("episodes"))
        self.assign_if_present(anime, "rating", merged.get("rating"))
        self.assign_if_present(anime, "studio", merged.get("studio"))
        self.assign_if_present(anime, "trailer_url", merged.get("trailer_url"))
        self.assign_if_present(anime, "members", merged.get("members"))
        self.assign_if_present(anime, "favorites", merged.get("favorites"))
        self.assign_if_present(anime, "rank", merged.get("rank"))
        self.assign_if_present(anime, "popularity", merged.get("popularity"))
        self.assign_if_present(anime, "aired_from", merged.get("aired_from"))
        self.assign_if_present(anime, "aired_to", merged.get("aired_to"))
        anime.notes = notes or anime.notes

        self.db.flush()
        anime.maple_score = calculate_maple_score(anime)
        return anime

    def assign_if_present(self, anime, field: str, value):
        if value is None:
            return

        if isinstance(value, str) and not value.strip():
            return

        setattr(anime, field, value)

    def choose_display_title(
        self,
        anime,
        searched_title: str,
        display_title: str | None,
        title_english: str | None,
    ) -> str | None:
        current_title = getattr(anime, "title", None)

        if not display_title:
            return current_title or searched_title

        if not current_title:
            return display_title

        if current_title == display_title:
            return current_title

        # Promote to a better display title when the current row was created
        # from a rough romaji/headline match and we later discover an official
        # English title.
        if (
            title_english
            and display_title == title_english
            and current_title in {
                searched_title,
                getattr(anime, "japanese_title", None),
            }
        ):
            title_taken = (
                self.db.query(Anime)
                .filter(Anime.title == display_title, Anime.id != anime.id)
                .first()
            )

            if not title_taken:
                return display_title

        return current_title


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

    anime.title = anime.title or title
    anime.title_english = item.get("title_english") or anime.title_english
    anime.japanese_title = item.get("title_japanese") or anime.japanese_title
    anime.anime_type = item.get("type") or anime.anime_type
    anime.episodes = item.get("episodes") or anime.episodes
    anime.status = (item.get("status") or "").lower() or anime.status or "announced"
    anime.release_season = item.get("season") or anime.release_season
    anime.release_year = item.get("year") or anime.release_year
    anime.synopsis = item.get("synopsis") or anime.synopsis
    anime.rating = item.get("rating") or anime.rating
    anime.score = item.get("score") if item.get("score") is not None else anime.score
    anime.rank = item.get("rank") if item.get("rank") is not None else anime.rank
    anime.popularity = (
        item.get("popularity") if item.get("popularity") is not None else anime.popularity
    )
    anime.members = item.get("members") if item.get("members") is not None else anime.members
    anime.favorites = (
        item.get("favorites") if item.get("favorites") is not None else anime.favorites
    )
    anime.genres = join_names(item.get("genres")) or anime.genres
    anime.studio = join_names(item.get("studios")) or anime.studio
    anime.poster_url = (
        jpg.get("large_image_url")
        or jpg.get("image_url")
        or anime.poster_url
    )
    anime.trailer_url = trailer.get("url") or anime.trailer_url
    anime.source_url = source_url or anime.source_url

    if hasattr(anime, "mal_id"):
        anime.mal_id = item.get("mal_id") or anime.mal_id

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
