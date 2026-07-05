import requests


ANILIST_API_URL = "https://graphql.anilist.co"
DEFAULT_TIMEOUT = 20

SEARCH_QUERY = """
query ($search: String) {
  Media(search: $search, type: ANIME) {
    title {
      romaji
      english
      native
    }
    description(asHtml: false)
    season
    seasonYear
    genres
    tags {
      name
      rank
    }
    episodes
    format
    status
    averageScore
    popularity
    favourites
    coverImage {
      extraLarge
      large
    }
    studios(isMain: true) {
      nodes {
        name
      }
    }
  }
}
"""


class AniListClient:
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout

    def search_anime(self, title: str):
        response = requests.post(
            ANILIST_API_URL,
            json={
                "query": SEARCH_QUERY,
                "variables": {"search": title},
            },
            timeout=self.timeout,
        )
        response.raise_for_status()

        payload = response.json()
        media = payload.get("data", {}).get("Media")

        if not media:
            return {}

        return self.normalize_anime(media)

    def normalize_anime(self, media: dict):
        title = media.get("title", {})
        cover = media.get("coverImage", {})
        studios = media.get("studios", {}).get("nodes", [])

        genres = ", ".join(media.get("genres", [])) or None
        studio_names = ", ".join(
            studio.get("name", "")
            for studio in studios
            if studio.get("name")
        ) or None

        tags = ", ".join(
            tag.get("name", "")
            for tag in media.get("tags", [])
            if tag.get("name") and (tag.get("rank") or 0) >= 50
        ) or None

        score = media.get("averageScore")
        if score is not None:
            score = round(score / 10, 2)

        status = self.normalize_status(media.get("status"))

        return {
            "display_title": title.get("english") or title.get("romaji"),
            "title_english": title.get("english"),
            "japanese_title": title.get("native"),
            "poster_url": cover.get("extraLarge") or cover.get("large"),
            "synopsis": media.get("description"),
            "score": score,
            "genres": genres,
            "themes": tags,
            "episodes": media.get("episodes"),
            "anime_type": media.get("format"),
            "popularity": media.get("popularity"),
            "favorites": media.get("favourites"),
            "studio": studio_names,
            "release_season": media.get("season"),
            "release_year": media.get("seasonYear"),
            "status": status,
        }

    def normalize_status(self, status: str | None):
        mapping = {
            "FINISHED": "finished",
            "RELEASING": "airing",
            "NOT_YET_RELEASED": "upcoming",
            "CANCELLED": "cancelled",
            "HIATUS": "hiatus",
        }
        return mapping.get(status or "", "announced")
