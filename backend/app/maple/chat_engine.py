import os

from app.maple.insight_engine import MapleInsightEngine
from app.maple.prompt_builder import MaplePromptBuilder
from app.maple.ai_engine import MapleAIEngine
from app.maple.preferences import MaplePreferences
from app.scout.event_service import ScoutEventService


class MapleChatEngine:
    COMPARISON_KEYWORDS = [
        "compare",
        "comparison",
        "versus",
        "vs",
        "better than",
        "better",
        "difference between",
    ]
    LIKE_PHRASES = [
        "i like",
        "i love",
        "my favorite",
        "i enjoyed",
        "i loved",
    ]
    DISLIKE_PHRASES = [
        "i hate",
        "i disliked",
        "i didn't enjoy",
        "i did not enjoy",
        "this wasn't for me",
        "this was not for me",
    ]

    def __init__(
        self,
        anime,
        news,
        history=None,
        summary=None,
        comparison_engine=None,
    ):
        self.anime = anime
        self.news = news or []
        self.history = history or []
        self.summary = summary
        self.comparison_engine = comparison_engine
        self.preferences = self.build_preferences()
        self.event_service = ScoutEventService()
        self.engine = MapleInsightEngine(anime=anime, news=self.news)
        self.ai_enabled = os.getenv("MAPLE_AI_ENABLED", "false").lower() == "true"

    def answer(self, question: str):
        rule_answer = self.rule_based_answer(question)

        if rule_answer:
            return rule_answer

        # Always try AI for custom questions.
        try:
            comparison_anime = self.find_comparison_anime(question)
            prompt = MaplePromptBuilder(
                anime=self.anime,
                comparison_anime=comparison_anime,
                news=self.news,
                history=self.history,
                summary=self.summary,
                preferences=self.preferences.summary(),
            ).build(question)

            return MapleAIEngine().answer(prompt)

        except Exception as error:
            print("Maple AI error:", repr(error))

            return (
                "Maple had trouble using AI for that question. "
                "Please check the backend logs for the OpenAI error."
            )

    def build_preferences(self):
        preferences = MaplePreferences()

        for message in self.history:
            self.update_preferences_from_text(
                preferences,
                getattr(message, "content", None) or message.get("content", ""),
            )

        return preferences

    def update_preferences_from_text(self, preferences, text: str):
        if not text:
            return

        q = text.lower()
        matched_titles = self.find_titles_in_text(text)

        if self.references_current_anime(q):
            matched_titles.append(getattr(self.anime, "title", None))

        normalized_titles = []
        seen = set()

        for title in matched_titles:
            if not title:
                continue

            normalized = title.strip()

            if not normalized:
                continue

            key = normalized.lower()

            if key in seen:
                continue

            seen.add(key)
            normalized_titles.append(normalized)

        if any(phrase in q for phrase in self.LIKE_PHRASES):
            for title in normalized_titles:
                preferences.add_like(title)

        if any(phrase in q for phrase in self.DISLIKE_PHRASES):
            for title in normalized_titles:
                preferences.add_dislike(title)

    def find_comparison_anime(self, question: str):
        q = question.lower()
        is_comparison = any(keyword in q for keyword in self.COMPARISON_KEYWORDS)

        if not is_comparison or not self.comparison_engine:
            return None

        matches = self.comparison_engine.find_titles(question)

        unique_matches = []
        seen_ids = set()

        for item in matches:
            item_id = getattr(item, "id", None)

            if item_id in seen_ids:
                continue

            seen_ids.add(item_id)
            unique_matches.append(item)

        current_id = getattr(self.anime, "id", None)
        non_current = [
            item for item in unique_matches if getattr(item, "id", None) != current_id
        ]

        if len(unique_matches) >= 2:
            if current_id is not None:
                current_match = next(
                    (item for item in unique_matches if getattr(item, "id", None) == current_id),
                    None,
                )

                if current_match and non_current:
                    return non_current[0]

            return unique_matches[1]

        if len(unique_matches) == 1:
            only_match = unique_matches[0]

            if getattr(only_match, "id", None) != current_id:
                return only_match

        return None

    def find_titles_in_text(self, text: str):
        if not self.comparison_engine:
            return []

        return [
            getattr(item, "title", None)
            for item in self.comparison_engine.find_titles(text)
        ]

    def references_current_anime(self, q: str):
        return any(
            phrase in q
            for phrase in [
                "i liked this",
                "i like this",
                "i loved this",
                "i love this",
                "i enjoyed this",
                "i hated this",
                "i dislike this",
                "i disliked this",
                "i didn't enjoy this",
                "i did not enjoy this",
                "this wasn't for me",
                "this was not for me",
                "my favorite is this",
            ]
        )

    def rule_based_answer(self, question: str):
        q = question.lower()

        if any(word in q for word in ["announcement", "recent", "update", "event"]):
            events = self.event_service.get_events_for_anime(self.anime.title)

            if events:
                latest = sorted(
                    events,
                    key=lambda event: event.importance,
                    reverse=True,
                )[0]

                return (
                    f"The biggest recent event is '{latest.event}'. "
                    f"{latest.summary} "
                    f"It was reported by {len(latest.sources)} source(s)."
                )

        if any(word in q for word in ["trend", "trending", "popular"]):
            return self.engine.anime_summary()

        if any(word in q for word in ["score", "rating", "maple score"]):
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

        if any(word in q for word in ["episode", "episodes"]):
            episodes = getattr(self.anime, "episodes", None)
            return (
                f"This series currently has {episodes} episodes."
                if episodes
                else "Episode information isn't available."
            )

        if any(word in q for word in ["status", "finished", "airing"]):
            status = getattr(self.anime, "status", None)
            return (
                f"The current release status is: {status}."
                if status
                else "Release status isn't available."
            )

        if any(word in q for word in ["studio", "studios", "animated", "animator"]):
            studios = getattr(self.anime, "studios", None) or getattr(
                self.anime, "studio", None
            )
            return (
                f"This anime was produced by {studios}."
                if studios
                else "Studio information isn't available."
            )

        return None
