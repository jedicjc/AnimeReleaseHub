from enum import Enum
import re


class ScoutCategory(str, Enum):
    SEASON = "Season Announcement"
    TRAILER = "Trailer"
    NEW_ANIME = "New Anime"
    DUB = "English Dub"
    SIMULDUB = "Simuldub"
    DUB_PREMIERE = "Dub Premiere"
    DUB_CAST = "Dub Cast"
    HOME_VIDEO_DUB = "Home Video Dub"
    MOVIE = "Movie"
    CASTING = "Casting"
    RELEASE = "Release Date"
    MANGA = "Manga"
    GAME = "Game"
    MERCH = "Merchandise"
    GENERAL = "General News"


CATEGORY_IMPORTANCE_BONUS = {
    ScoutCategory.SEASON: 40,
    ScoutCategory.TRAILER: 25,
    ScoutCategory.DUB: 20,
    ScoutCategory.SIMULDUB: 20,
    ScoutCategory.DUB_PREMIERE: 22,
    ScoutCategory.DUB_CAST: 18,
    ScoutCategory.HOME_VIDEO_DUB: 20,
    ScoutCategory.MOVIE: 30,
}

MAJOR_STUDIOS = {
    "a-1 pictures",
    "bones",
    "cloverworks",
    "doga kobo",
    "kyoto animation",
    "lerche",
    "madhouse",
    "mappa",
    "production i.g",
    "satelight",
    "science saru",
    "shaft",
    "studio bind",
    "studio deen",
    "studio ghibli",
    "studio pierrot",
    "sunrise",
    "toei animation",
    "trigger",
    "ufotable",
    "wit studio",
}

_CATEGORY_ALIASES = {
    "season": ScoutCategory.SEASON,
    "season announcement": ScoutCategory.SEASON,
    "sequel": ScoutCategory.SEASON,
    "trailer": ScoutCategory.TRAILER,
    "promo": ScoutCategory.TRAILER,
    "promotional video": ScoutCategory.TRAILER,
    "teaser": ScoutCategory.TRAILER,
    "new anime": ScoutCategory.NEW_ANIME,
    "new_adaptation": ScoutCategory.NEW_ANIME,
    "tv anime adaptation": ScoutCategory.NEW_ANIME,
    "dub": ScoutCategory.DUB,
    "dub_update": ScoutCategory.DUB,
    "english dub": ScoutCategory.DUB,
    "simuldub": ScoutCategory.SIMULDUB,
    "dub premiere": ScoutCategory.DUB_PREMIERE,
    "dub cast": ScoutCategory.DUB_CAST,
    "home video dub": ScoutCategory.HOME_VIDEO_DUB,
    "blu ray dub": ScoutCategory.HOME_VIDEO_DUB,
    "home video release": ScoutCategory.HOME_VIDEO_DUB,
    "movie": ScoutCategory.MOVIE,
    "film": ScoutCategory.MOVIE,
    "casting": ScoutCategory.CASTING,
    "cast": ScoutCategory.CASTING,
    "cast_update": ScoutCategory.CASTING,
    "release": ScoutCategory.RELEASE,
    "release date": ScoutCategory.RELEASE,
    "manga": ScoutCategory.MANGA,
    "game": ScoutCategory.GAME,
    "merch": ScoutCategory.MERCH,
    "merchandise": ScoutCategory.MERCH,
    "general": ScoutCategory.GENERAL,
    "general news": ScoutCategory.GENERAL,
}


def clamp_score(value, default=0) -> int:
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        score = default

    return max(0, min(100, score))


def normalize_category(value) -> ScoutCategory:
    if isinstance(value, ScoutCategory):
        return value

    if not value:
        return ScoutCategory.GENERAL

    normalized = str(value).strip()

    for category in ScoutCategory:
        if normalized.lower() == category.value.lower():
            return category

    key = re.sub(r"[^a-z0-9]+", " ", normalized.lower()).strip()
    return _CATEGORY_ALIASES.get(key, ScoutCategory.GENERAL)


def classify_article(title: str = "", summary: str = "") -> ScoutCategory:
    text = f"{title or ''} {summary or ''}".lower()

    if "simuldub" in text:
        return ScoutCategory.SIMULDUB
    if "dub cast" in text or "english cast" in text:
        return ScoutCategory.DUB_CAST
    if "home video dub" in text or "blu-ray dub" in text or "blu ray dub" in text:
        return ScoutCategory.HOME_VIDEO_DUB
    if "dub premiere" in text or "dubbed premiere" in text:
        return ScoutCategory.DUB_PREMIERE
    if "english dub" in text or re.search(r"\bdub(?:bed|s)?\b", text):
        return ScoutCategory.DUB
    if "trailer" in text or "teaser" in text or "promo" in text or "pv" in text:
        return ScoutCategory.TRAILER
    if "movie" in text or "film" in text:
        return ScoutCategory.MOVIE
    if "season" in text or "sequel" in text:
        return ScoutCategory.SEASON
    if "release date" in text or "premiere" in text or "debuts" in text:
        return ScoutCategory.RELEASE
    if "cast" in text or "voice actor" in text:
        return ScoutCategory.CASTING
    if "manga" in text:
        return ScoutCategory.MANGA
    if "game" in text:
        return ScoutCategory.GAME
    if "merch" in text or "figure" in text or "blu-ray" in text:
        return ScoutCategory.MERCH
    if "anime adaptation" in text or "gets anime" in text or "tv anime" in text:
        return ScoutCategory.NEW_ANIME

    return ScoutCategory.GENERAL


def has_major_studio(article_text: str = "", studio: str | None = None) -> bool:
    values = [article_text or "", studio or ""]
    haystack = " ".join(values).lower()

    return any(studio_name in haystack for studio_name in MAJOR_STUDIOS)


def calculate_importance(
    category,
    ai_importance=None,
    confidence=None,
    article_text: str = "",
    studio: str | None = None,
) -> int:
    scout_category = normalize_category(category)
    base = CATEGORY_IMPORTANCE_BONUS.get(scout_category, 5)

    if has_major_studio(article_text=article_text, studio=studio):
        base += 15

    ai_component = clamp_score(ai_importance, default=50) * 0.35
    confidence_component = clamp_score(confidence, default=50) * 0.25

    return clamp_score(base + ai_component + confidence_component)


def detect_event_type(title: str = "", summary: str = "", category=None) -> str:
    text = f"{title or ''} {summary or ''}".lower()

    if "trailer" in text or "teaser" in text or "promo" in text or "pv" in text:
        return ScoutCategory.TRAILER.value

    scout_category = normalize_category(category or classify_article(title, summary))

    if scout_category in {
        ScoutCategory.DUB,
        ScoutCategory.SIMULDUB,
        ScoutCategory.DUB_PREMIERE,
        ScoutCategory.DUB_CAST,
        ScoutCategory.HOME_VIDEO_DUB,
    }:
        return ScoutCategory.DUB.value
    if scout_category == ScoutCategory.SEASON:
        return ScoutCategory.SEASON.value
    if scout_category == ScoutCategory.MOVIE:
        return ScoutCategory.MOVIE.value
    if scout_category == ScoutCategory.RELEASE:
        return ScoutCategory.RELEASE.value
    if scout_category == ScoutCategory.NEW_ANIME:
        return ScoutCategory.NEW_ANIME.value

    return scout_category.value


def extract_season_label(title: str = "", summary: str = "") -> str:
    text = f"{title or ''} {summary or ''}"

    numeric_match = re.search(r"\bseason\s+(\d+)\b", text, flags=re.IGNORECASE)
    if numeric_match:
        return f"Season {numeric_match.group(1)}"

    ordinal_match = re.search(
        r"\b(second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+season\b",
        text,
        flags=re.IGNORECASE,
    )

    if ordinal_match:
        ordinals = {
            "second": "2",
            "third": "3",
            "fourth": "4",
            "fifth": "5",
            "sixth": "6",
            "seventh": "7",
            "eighth": "8",
            "ninth": "9",
            "tenth": "10",
        }
        return f"Season {ordinals[ordinal_match.group(1).lower()]}"

    return ""


def canonical_event_name(
    anime_title: str | None,
    category,
    title: str = "",
    summary: str = "",
    fallback_event: str | None = None,
) -> str:
    event_type = detect_event_type(title, summary, category)

    if anime_title:
        season_label = extract_season_label(title, summary)
        parts = [anime_title.strip()]

        if season_label and season_label.lower() not in anime_title.lower():
            parts.append(season_label)

        if event_type != ScoutCategory.GENERAL.value:
            parts.append(event_type)

        return " ".join(parts).strip()

    if fallback_event:
        return str(fallback_event).strip()

    return event_type


def event_key(value: str | None) -> str:
    if not value:
        return ""

    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def event_family_key(value: str | None) -> str:
    key = event_key(value)
    key = re.sub(r"\bseason\s+\d+\b", "", key)
    key = re.sub(r"\s+", " ", key)

    return key.strip()


def event_seasons(value: str | None) -> set[str]:
    return set(re.findall(r"\bseason\s+\d+\b", event_key(value)))
