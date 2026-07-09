from __future__ import annotations

import re


INVALID_NEWS_TITLES = {
    "html",
    "body",
    "head",
    "script",
    "noscript",
    "div",
    "span",
    "style",
    "meta",
    "link",
}


def is_valid_news_title(title: str | None) -> bool:
    if not title:
        return False

    normalized = re.sub(r"\s+", " ", title).strip().lower()

    if not normalized:
        return False

    if normalized in INVALID_NEWS_TITLES:
        return False

    if normalized.startswith("<") or normalized.endswith(">"):
        return False

    if len(normalized) < 4:
        return False

    return True
