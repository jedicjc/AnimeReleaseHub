class MaplePromptBuilder:
    FIELD_ALIASES = {
        "title_japanese": "japanese_title",
        "type": "anime_type",
        "season": "release_season",
        "year": "release_year",
        "studios": "studio",
    }

    def __init__(self, anime, news):
        self.anime = anime
        self.news = news or []

    def value(self, field: str, fallback: str = "Unknown"):
        value = getattr(self.anime, field, None)

        if isinstance(value, str):
            value = value.strip()

        if value is None or value == "":
            alias = self.FIELD_ALIASES.get(field)

            if alias:
                value = getattr(self.anime, alias, None)

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

Recent News:
{self.build_news_context()}

Rules:
- Answer only using the anime information and recent news above.
- If the data is missing, say Maple does not have that information yet.
- If the user asks why it is trending, mention Maple Score, popularity, members, favorites, status, and recent news when available.
- If the user asks whether it is worth watching, explain who might enjoy it based on genres, synopsis, score, and popularity.
- If the user asks about news, summarize the recent news list.
- Keep the answer to 2-4 short paragraphs.
- Speak as Maple.

User Question:
{question}
""".strip()
