import os

import requests

from app.scout.providers.base import ScoutProvider


class AnimeDubUpdatesProvider(ScoutProvider):
    name = "animedubupdates"
    provider_type = "news"

    BASE_URL = "https://api.x.com/2"

    def __init__(self):
        self.token = os.getenv("X_BEARER_TOKEN")
        self.username = (
            os.getenv("ANIMEDUBUPDATES_USERNAME")
            or os.getenv("ANIMEDUBHUB_USERNAME")
            or "AnimeDubUpdates"
        )

    def fetch(self, limit=25):
        if not self.token:
            raise RuntimeError("Missing X_BEARER_TOKEN")

        user = self._lookup_user()
        tweets = self._fetch_tweets(user["id"], limit=limit)

        return [
            {
                "title": tweet["text"][:120],
                "summary": tweet["text"],
                "url": f"https://x.com/{self.username}/status/{tweet['id']}",
                "source": "AnimeDubUpdates",
                "published_at": tweet.get("created_at"),
            }
            for tweet in tweets
        ]

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
        }

    def _lookup_user(self):
        response = requests.get(
            f"{self.BASE_URL}/users/by/username/{self.username}",
            headers=self._headers(),
            timeout=20,
        )

        response.raise_for_status()
        return response.json()["data"]

    def _fetch_tweets(self, user_id, limit):
        response = requests.get(
            f"{self.BASE_URL}/users/{user_id}/tweets",
            headers=self._headers(),
            params={
                "max_results": max(5, min(limit, 100)),
                "tweet.fields": "created_at",
            },
            timeout=20,
        )

        response.raise_for_status()
        return response.json().get("data", [])


# Backward-compatible alias for older imports.
AnimeDubHubProvider = AnimeDubUpdatesProvider
