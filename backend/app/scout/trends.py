from app.scout.article_classifier import (
    CATEGORY_IMPORTANCE_BONUS,
    ScoutCategory,
    normalize_category,
)


def category_weight(category: str | None) -> int:
    scout_category = normalize_category(category)

    if scout_category in CATEGORY_IMPORTANCE_BONUS:
        return CATEGORY_IMPORTANCE_BONUS[scout_category]
    if scout_category == ScoutCategory.NEW_ANIME:
        return 20
    if scout_category == ScoutCategory.CASTING:
        return 12
    if scout_category == ScoutCategory.RELEASE:
        return 18
    if scout_category in {ScoutCategory.MANGA, ScoutCategory.GAME}:
        return 10
    if scout_category == ScoutCategory.MERCH:
        return 6

    return 5


def calculate_trend_score(article_category: str | None, anime_score: float | None):
    score = 0

    score += category_weight(article_category)

    if anime_score:
        score += anime_score * 5

    return round(max(score, 0), 2)
