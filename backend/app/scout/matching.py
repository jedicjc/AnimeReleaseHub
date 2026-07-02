from difflib import SequenceMatcher


ALLOWED_ANIME_TYPES = {
    "TV",
    "Movie",
    "ONA",
    "OVA",
    "Special",
}


def normalize_title(title: str | None) -> str:
    if not title:
        return ""

    return (
        title.lower()
        .replace(":", "")
        .replace("-", " ")
        .replace("_", " ")
        .replace("'", "")
        .replace('"', "")
        .strip()
    )


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(
        None,
        normalize_title(a),
        normalize_title(b),
    ).ratio()


def is_good_jikan_match(
    searched_title: str,
    jikan_anime: dict,
    minimum_score: float = 0.58,
) -> bool:
    anime_type = jikan_anime.get("type")

    if anime_type and anime_type not in ALLOWED_ANIME_TYPES:
        return False

    candidate_titles = [
        jikan_anime.get("title"),
        jikan_anime.get("title_english"),
        jikan_anime.get("title_japanese"),
    ]

    for title in candidate_titles:
        if title and title_similarity(searched_title, title) >= minimum_score:
            return True

    for title_obj in jikan_anime.get("titles", []):
        title = title_obj.get("title")
        if title and title_similarity(searched_title, title) >= minimum_score:
            return True

    return False
