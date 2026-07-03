import os

from app.maple.insight_engine import MapleInsightEngine
from app.maple.prompt_builder import MaplePromptBuilder
from app.maple.ai_engine import MapleAIEngine


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
        rule_answer = self.rule_based_answer(question)

        if rule_answer:
            return rule_answer

        print("MAPLE_AI_ENABLED:", self.ai_enabled)

        if self.ai_enabled:
            try:
                prompt = MaplePromptBuilder(
                    anime=self.anime,
                    news=self.news,
                ).build(question)

                return MapleAIEngine().answer(prompt)

            except Exception as error:
                print("Maple AI error:", repr(error))

        return (
            "I'm still learning! Try asking about trends, scores, "
            "recommendations, recent news, episodes, studios, or status."
        )

    def rule_based_answer(self, question: str):
        q = question.lower()

        if any(word in q for word in ["trend", "trending", "popular"]):
            return self.engine.anime_summary()

        if any(word in q for word in ["worth", "watch", "good"]):
            score = getattr(self.anime, "trend_score", 0) or 0

            if score >= 90:
                return (
                    "Absolutely. This is currently one of the hottest anime "
                    "and has extremely strong community momentum."
                )

            if score >= 75:
                return "Yes. It has solid momentum and is well worth checking out."

            return (
                "It may appeal to fans of its genre, although it isn't "
                "currently among the strongest trending titles."
            )

        if any(word in q for word in ["recommend", "similar", "enjoy"]):
            genres = getattr(self.anime, "genres", "") or "this genre"

            return f"If you enjoy {genres}, this title is likely a great fit."

        if any(word in q for word in ["score", "rating"]):
            explanations = self.engine.score_explanation()

            if isinstance(explanations, list):
                return " ".join(explanations)

            return explanations

        if "news" in q:
            if not self.news:
                return "No recent news is available."

            latest = self.news[0]
            latest_title = getattr(latest, "title", "Untitled article")

            return (
                f"There are {len(self.news)} recent news articles. "
                f"The latest is titled '{latest_title}'."
            )

        if any(phrase in q for phrase in [
            "what's the story",
            "what is the story",
            "synopsis",
            "plot summary",
            "what is it about",
            "what's it about",
        ]):
            synopsis = getattr(self.anime, "synopsis", None)

            if synopsis:
                return synopsis

            return "Story information isn't available."

        if any(word in q for word in ["episode", "episodes"]):
            episodes = getattr(self.anime, "episodes", None)

            if episodes:
                return f"This series currently has {episodes} episodes."

            return "Episode information isn't available."

        if any(word in q for word in ["status", "finished", "airing"]):
            status = getattr(self.anime, "status", None)

            if status:
                return f"The current release status is: {status}."

            return "Release status isn't available."

        if any(word in q for word in ["studio", "studios", "animated", "animator"]):
            studios = (
                getattr(self.anime, "studios", None)
                or getattr(self.anime, "studio", None)
            )

            if studios:
                return f"This anime was produced by {studios}."

            return "Studio information isn't available."

        if any(word in q for word in ["genre", "genres"]):
            genres = getattr(self.anime, "genres", None)

            if genres:
                return f"This anime belongs to: {genres}."

            return "Genre information isn't available."

        if any(word in q for word in ["favorite", "favorites"]):
            favorites = getattr(self.anime, "favorites", None)

            if favorites:
                return (
                    f"This anime has {favorites:,} users who marked it "
                    "as a favorite."
                )

            return "Favorite count isn't available."

        return None
