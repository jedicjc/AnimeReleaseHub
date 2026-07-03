import os

from app.maple.ai_engine import MapleAIEngine
from app.maple.insight_engine import MapleInsightEngine
from app.maple.prompt_builder import MaplePromptBuilder


class MapleChatEngine:
    def __init__(self, anime, news):
        self.anime = anime
        self.news = news or []

        self.engine = MapleInsightEngine(
            anime=anime,
            news=self.news,
        )

        self.ai_enabled = os.getenv("MAPLE_AI_ENABLED", "false").lower() == "true"

    def answer(self, question: str):
        if self.ai_enabled:
            try:
                prompt = MaplePromptBuilder(
                    anime=self.anime,
                    news=self.news,
                ).build(question)

                return MapleAIEngine().answer(prompt)

            except NotImplementedError:
                return self.rule_based_answer(question)

            except Exception:
                return self.rule_based_answer(question)

        return self.rule_based_answer(question)

    def rule_based_answer(self, question: str):
        q = question.lower()

        if any(word in q for word in ["trend", "trending", "popular"]):
            return self.engine.anime_summary()

        if any(word in q for word in ["worth", "watch", "good"]):
            score = getattr(self.engine.anime, "trend_score", 0) or 0

            if score >= 90:
                return (
                    "Absolutely. This is currently one of the hottest anime "
                    "and has extremely strong community momentum."
                )

            if score >= 75:
                return (
                    "Yes. It has solid momentum and is well worth checking out."
                )

            return (
                "It may appeal to fans of its genre, although it isn't "
                "currently among the strongest trending titles."
            )

        if any(word in q for word in ["recommend", "similar", "enjoy"]):
            genres = getattr(self.engine.anime, "genres", "") or "this genre"

            return f"If you enjoy {genres}, this title is likely a great fit."

        if any(word in q for word in ["score", "rating"]):
            explanations = self.engine.score_explanation()

            if explanations:
                return " ".join(explanations)

            return (
                "Maple Score is based on trend momentum, community rating, "
                "popularity, members, favorites, trailers, and release status."
            )

        if "news" in q:
            if not self.engine.news:
                return "No recent news is available."

            latest = self.engine.news[0]

            return (
                f"There are {len(self.engine.news)} recent news articles. "
                f"The latest is titled '{latest.title}'."
            )

        if any(word in q for word in ["story", "about", "synopsis", "plot"]):
            synopsis = getattr(self.engine.anime, "synopsis", None)

            if synopsis:
                return synopsis

            return "Story information isn't available."

        if any(word in q for word in ["genre", "genres"]):
            genres = getattr(self.engine.anime, "genres", None)

            if genres:
                return f"This anime belongs to: {genres}."

            return "Genre information isn't available."

        if any(word in q for word in ["studio", "made", "developer", "animated"]):
            studio = getattr(self.engine.anime, "studio", None)

            if studio:
                return f"This anime was produced by {studio}."

            return "Studio information isn't available."

        if any(word in q for word in ["episode", "episodes"]):
            episodes = getattr(self.engine.anime, "episodes", None)

            if episodes:
                return f"This series currently has {episodes} episodes."

            return "Episode information isn't available."

        if any(word in q for word in ["status", "finished", "airing"]):
            status = getattr(self.engine.anime, "status", None)

            if status:
                return f"The current release status is: {status}."

            return "Release status isn't available."

        if any(word in q for word in ["favorite", "favorites"]):
            favorites = getattr(self.engine.anime, "favorites", None)

            if favorites:
                return (
                    f"This anime has {favorites:,} users who marked it "
                    "as a favorite."
                )

            return "Favorite count isn't available."

        return (
            "I'm still learning! Try asking about trends, "
            "scores, recommendations, or recent news."
        )
