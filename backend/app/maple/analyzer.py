def calculate_hype(anime):
    score = 0

    if anime.score:
        score += anime.score * 10

    if anime.poster_url:
        score += 10

    if anime.status == "upcoming":
        score += 20

    if anime.genres:
        if "Action" in anime.genres:
            score += 10
        if "Fantasy" in anime.genres:
            score += 8

    return min(score, 100)


def get_audience_type(anime):
    genres = (anime.genres or "").lower()

    if "action" in genres:
        return "Action Fans"
    if "romance" in genres:
        return "Romance Viewers"
    if "fantasy" in genres:
        return "Fantasy Fans"
    if "sci-fi" in genres:
        return "Sci-Fi Audience"

    return "General Audience"


def build_maple_insight(anime):
    parts = []

    if anime.score and anime.score >= 8:
        parts.append("Highly rated by the community")

    if anime.status == "announced":
        parts.append("Recently announced title gaining attention")

    if anime.poster_url:
        parts.append("Has official promotional visuals")

    if anime.genres:
        parts.append(f"Strong presence in {anime.genres}")

    if not parts:
        parts.append("Standard tracked title with moderate interest")

    return " • ".join(parts)