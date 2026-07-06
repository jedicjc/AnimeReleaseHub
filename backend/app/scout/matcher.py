import re

from app.database.models import Anime


def clean_text(value: str) -> str:
    if not value:
        return ""

    value = value.lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


class ScoutMatcher:
    def __init__(self, db):
        self.db = db

    def anime_titles(self, anime):
        return [
            getattr(anime, "title", None),
            getattr(anime, "title_english", None),
            getattr(anime, "japanese_title", None),
            getattr(anime, "title_japanese", None),
        ]

    def find_anime_for_news(self, title: str, summary: str = ""):
        search_text = clean_text(f"{title} {summary}")

        if not search_text:
            return None

        anime_list = self.db.query(Anime).all()

        best_match = None
        best_score = 0

        for anime in anime_list:
            for possible_title in self.anime_titles(anime):
                cleaned_title = clean_text(possible_title)

                if not cleaned_title:
                    continue

                if cleaned_title in search_text:
                    score = len(cleaned_title)

                    if score > best_score:
                        best_score = score
                        best_match = anime

        return best_match
