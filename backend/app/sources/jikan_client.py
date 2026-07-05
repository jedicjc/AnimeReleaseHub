import time

import requests

from app.scout.config import REQUEST_TIMEOUT
from app.scout.matching import is_good_jikan_match
from app.scout.sources import HEADERS


class JikanClient:
    BASE_URL = "https://api.jikan.moe/v4"

    def __init__(self, delay: float = 0.7, timeout: int = REQUEST_TIMEOUT):
        self.delay = delay
        self.timeout = timeout

    def get(self, path: str, params=None):
        time.sleep(self.delay)

        response = requests.get(
            f"{self.BASE_URL}{path}",
            params=params or {},
            timeout=self.timeout,
            headers=HEADERS,
        )
        response.raise_for_status()
        return response.json()

    def top_anime(self, page: int = 1, limit: int = 25):
        return self.get(
            "/top/anime",
            params={
                "page": page,
                "limit": limit,
                "sfw": "true",
            },
        )

    def current_season(self, page: int = 1, limit: int = 25):
        return self.get(
            "/seasons/now",
            params={
                "page": page,
                "limit": limit,
                "sfw": "true",
            },
        )

    def enrich_title(self, title: str):
        payload = self.get(
            "/anime",
            params={"q": title, "limit": 1, "sfw": "true"},
        )
        results = payload.get("data", [])

        if not results:
            return {}

        anime = results[0]

        if not is_good_jikan_match(title, anime):
            return {}

        return self.normalize_anime(title, anime)

    def normalize_anime(self, title: str, anime: dict):
        images = anime.get("images", {})
        jpg = images.get("jpg", {})
        trailer = anime.get("trailer", {})
        aired = anime.get("aired", {})

        genres = ", ".join(
            genre.get("name", "")
            for genre in anime.get("genres", [])
            if genre.get("name")
        ) or None

        studios = ", ".join(
            studio.get("name", "")
            for studio in anime.get("studios", [])
            if studio.get("name")
        ) or None

        return {
            "display_title": anime.get("title_english") or anime.get("title") or title,
            "japanese_title": anime.get("title_japanese"),
            "poster_url": jpg.get("large_image_url") or jpg.get("image_url"),
            "synopsis": anime.get("synopsis"),
            "score": anime.get("score"),
            "genres": genres,
            "episodes": anime.get("episodes"),
            "anime_type": anime.get("type"),
            "rating": anime.get("rating"),
            "members": anime.get("members"),
            "favorites": anime.get("favorites"),
            "rank": anime.get("rank"),
            "popularity": anime.get("popularity"),
            "trailer_url": trailer.get("url"),
            "studio": studios,
            "aired_from": aired.get("from"),
            "aired_to": aired.get("to"),
            "release_season": anime.get("season"),
            "release_year": anime.get("year"),
            "status": (anime.get("status") or "").lower() or "announced",
            "source_url": anime.get("url"),
        }
