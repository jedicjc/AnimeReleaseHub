import time

import requests

from app.scout.providers.base import ScoutProvider
from app.scout.sources import HEADERS


class JikanProvider(ScoutProvider):
    name = "jikan"
    provider_type = "anime"
    BASE_URL = "https://api.jikan.moe/v4"

    def __init__(
        self,
        delay: float = 0.7,
        timeout: int = 30,
        retries: int = 3,
        retry_backoff: float = 2.0,
    ):
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self.retry_backoff = retry_backoff

    def get(self, path, params=None):
        params = params or {}
        last_error = None

        for attempt in range(3):
            try:
                time.sleep(self.delay)

                response = requests.get(
                    f"{self.BASE_URL}{path}",
                    params=params,
                    timeout=30,
                    headers=HEADERS,
                )

                response.raise_for_status()
                return response.json()

            except requests.RequestException as error:
                last_error = error
                time.sleep(self.retry_backoff * (attempt + 1))

        raise last_error

    def fetch_top_anime(self, page=1, limit=25):
        return self.get(
            "/top/anime",
            {
                "page": page,
                "limit": limit,
                "sfw": "true",
            },
        ).get("data", [])

    def fetch_current_season(self, page=1, limit=25):
        return self.get(
            "/seasons/now",
            {
                "page": page,
                "limit": limit,
                "sfw": "true",
            },
        ).get("data", [])

    def fetch(self, limit=25):
        try:
            return self.fetch_top_anime(page=1, limit=limit)
        except requests.RequestException:
            return self.fetch_current_season(page=1, limit=limit)

    def health_check(self):
        try:
            items = self.fetch_current_season(page=1, limit=1)
            return {
                "provider": self.name,
                "status": "healthy",
                "sample_count": len(items),
                "endpoint": "seasons/now",
            }
        except Exception as season_error:
            try:
                items = self.fetch_top_anime(page=1, limit=1)
                return {
                    "provider": self.name,
                    "status": "degraded",
                    "sample_count": len(items),
                    "endpoint": "top/anime",
                    "message": f"season endpoint unavailable: {season_error}",
                }
            except Exception as top_error:
                return {
                    "provider": self.name,
                    "status": "error",
                    "message": str(top_error),
                }
