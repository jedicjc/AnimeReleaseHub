import time

import requests

from app.scout.config import REQUEST_TIMEOUT
from app.scout.sources import HEADERS


class JikanProvider:
    BASE_URL = "https://api.jikan.moe/v4"

    def __init__(self, delay: float = 0.7, timeout: int = REQUEST_TIMEOUT):
        self.delay = delay
        self.timeout = timeout

    def get(self, path, params=None):
        time.sleep(self.delay)

        response = requests.get(
            f"{self.BASE_URL}{path}",
            params=params or {},
            timeout=self.timeout,
            headers=HEADERS,
        )

        response.raise_for_status()
        return response.json()

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
