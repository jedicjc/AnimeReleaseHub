def category_weight(category: str | None) -> int:
    if category == "trailer":
        return 25
    if category == "sequel":
        return 22
    if category == "new_adaptation":
        return 20
    if category == "cast_update":
        return 12
    if category == "staff_update":
        return 10
    if category == "dub_update":
        return 8
    if category == "delay":
        return -10

    return 5


def calculate_trend_score(article_category: str | None, anime_score: float | None):
    score = 0

    score += category_weight(article_category)

    if anime_score:
        score += anime_score * 5

    return round(max(score, 0), 2)
