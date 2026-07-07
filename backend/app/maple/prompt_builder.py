class MaplePromptBuilder:
    FIELD_ALIASES = {
        "title_japanese": "japanese_title",
        "type": "anime_type",
        "season": "release_season",
        "year": "release_year",
        "studios": "studio",
    }

    def __init__(
        self,
        anime,
        news,
        history=None,
        summary=None,
        comparison_anime=None,
        preferences=None,
    ):
        self.anime = anime
        self.news = news or []
        self.history = history or []
        self.summary = summary
        self.comparison_anime = comparison_anime
        self.preferences = preferences or {"likes": [], "dislikes": []}

    def value(self, field: str, fallback: str = "Unknown", anime=None):
        source_anime = anime or self.anime
        value = getattr(source_anime, field, None)

        if isinstance(value, str):
            value = value.strip()

        if value is None or value == "":
            alias = self.FIELD_ALIASES.get(field)

            if alias:
                value = getattr(source_anime, alias, None)

                if isinstance(value, str):
                    value = value.strip()

        if value is None or value == "":
            return fallback

        return value

    def build_news_context(self) -> str:
        if not self.news:
            return "No recent news available."

        lines = []

        for index, article in enumerate(self.news, start=1):
            title = getattr(article, "title", "Untitled article")
            source = getattr(article, "source", "Unknown source")
            url = getattr(article, "url", "")

            lines.append(
                f"{index}. Title: {title}\n"
                f"   Source: {source}\n"
                f"   URL: {url}"
            )

        return "\n".join(lines)

    def build_history(self) -> str:
        if not self.history:
            return "No previous conversation."

        lines = []

        for msg in self.history[-10:]:
            if hasattr(msg, "model_dump"):
                msg = msg.model_dump()

            role = msg.get("role", "user")
            content = msg.get("content", "")
            lines.append(f"{role.title()}: {content}")

        return "\n".join(lines)

    def build_summary(self) -> str:
        if not self.summary:
            return "No previous summary."

        return self.summary

    def build_comparison_context(self) -> str:
        if not self.comparison_anime:
            return "No comparison anime supplied."

        return f"""
Title: {self.value("title", anime=self.comparison_anime)}
Genres: {self.value("genres", anime=self.comparison_anime)}
Synopsis: {self.value("synopsis", anime=self.comparison_anime)}
Maple Score: {self.value("maple_score", anime=self.comparison_anime)}
Popularity: {self.value("popularity", anime=self.comparison_anime)}
Members: {self.value("members", anime=self.comparison_anime)}
Favorites: {self.value("favorites", anime=self.comparison_anime)}
Status: {self.value("status", anime=self.comparison_anime)}
Episodes: {self.value("episodes", anime=self.comparison_anime)}
""".strip()

    def build_preferences_context(self) -> str:
        likes = self.preferences.get("likes", [])
        dislikes = self.preferences.get("dislikes", [])

        like_lines = "\n".join(f"- {item}" for item in likes) or "- None yet"
        dislike_lines = "\n".join(f"- {item}" for item in dislikes) or "- None yet"

        return f"""
Likes:
{like_lines}

Dislikes:
{dislike_lines}
""".strip()

    def build(self, question: str) -> str:
        return f"""
You are Maple, the anime assistant for AnimeReleaseHub.

Personality:
- Friendly, helpful, and knowledgeable.
- Clear and concise.
- Honest when information is missing.
- Do not invent facts.
- Do not spoil major plot points unless the user asks.

Anime Information:
Title: {self.value("title")}
English Title: {self.value("title_english")}
Japanese Title: {self.value("title_japanese")}
Type: {self.value("type")}
Episodes: {self.value("episodes")}
Status: {self.value("status")}
Season: {self.value("season")}
Year: {self.value("year")}
Studios: {self.value("studios")}
Genres: {self.value("genres")}
Themes: {self.value("themes")}
Rating: {self.value("rating")}
Popularity: {self.value("popularity")}
Members: {self.value("members")}
Favorites: {self.value("favorites")}
Maple Score: {self.value("maple_score")}
Trend Score: {self.value("trend_score")}
Synopsis: {self.value("synopsis")}

Comparison Anime:
{self.build_comparison_context()}

User Preferences:
{self.build_preferences_context()}

Recent News:
{self.build_news_context()}

Conversation Summary:
{self.build_summary()}

Recent Conversation:
{self.build_history()}

Memory Rules:
- Use the previous conversation to understand follow-up questions.
- If the user says "it", "this one", "which one", or similar, infer what they mean from the conversation history.
- Do not ask the user to repeat something already mentioned.

Knowledge Rules:
- Use Maple's anime data as the primary source.
- If the user compares this anime to another well-known anime, you may use general anime knowledge for the other title.
- Do not invent statistics, scores, release dates, staff, or news.
- Clearly say when Maple does not have database information for the other title.

Comparison Rules:
- If two anime are supplied, compare them directly.
- Discuss strengths and weaknesses of each.
- Mention differences in pacing, tone, themes, and audience.
- If one excels in a category, explain why.
- Do not automatically declare a winner; justify your conclusions.

Style Rules:
- Do not start every answer with "Hi, I'm Maple."
- Do not prefix answers with "Maple:".
- Be warm, helpful, and concise.
- Use 1-3 short paragraphs unless the user asks for a specific format.

If the user asks for recommendations:
- Explain why.
- Mention genres.
- Mention pacing.
- Mention tone.
- Mention audience.
- Keep spoilers minimal.
- Prefer anime similar to liked titles.
- Avoid recommending disliked titles.
- Offer 3 recommendations unless the user asks otherwise.

Before answering:
1. Make sure you answered the user's actual question.
2. Check if the conversation already established context.
3. Avoid repeating yourself.
4. If comparing anime, explain similarities AND differences.
5. If uncertain, say so instead of guessing.

Current User Question:
{question}
""".strip()
