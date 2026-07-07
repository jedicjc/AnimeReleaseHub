import time

import requests

from app.scout.config import REQUEST_TIMEOUT
from app.scout.providers.base import ScoutProvider
from app.scout.sources import HEADERS


class JikanProvider(ScoutProvider):
    name = "jikan"
    provider_type = "anime"
    BASE_URL = "https://api.jikan.moe/v4"

    def __init__(
        self,
        delay: float = 0.7,
        timeout: int = REQUEST_TIMEOUT,
        retries: int = 3,
        retry_backoff: float = 1.25,
    ):
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self.retry_backoff = retry_backoff

    def get(self, path, params=None):
        last_error = None

        for attempt in range(1, self.retries + 1):
            time.sleep(self.delay)

            try:
                response = requests.get(
                    f"{self.BASE_URL}{path}",
                    params=params or {},
                    timeout=self.timeout,
                    headers=HEADERS,
                )

                response.raise_for_status()
                return response.json()

            except requests.HTTPError as error:
                last_error = error
                status_code = getattr(error.response, "status_code", None)
                should_retry = status_code is not None and status_code >= 500

                if attempt >= self.retries or not should_retry:
                    raise

            except requests.RequestException as error:
                last_error = error

                if attempt >= self.retries:
                    raise

            time.sleep(self.retry_backoff * attempt)

        if last_error:
            raise last_error

        raise RuntimeError("Jikan request failed without an error")

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
        return self.fetch_top_anime(page=1, limit=limit)
