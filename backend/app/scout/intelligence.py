import json
import re

from app.maple.ai_engine import MapleAIEngine
from app.scout.article_classifier import (
    ScoutCategory,
    calculate_importance,
    classify_article,
    clamp_score,
    normalize_category,
)


def _extract_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)

        if not match:
            raise

        return json.loads(match.group(0))


def _normalize_tags(raw_tags) -> list[str]:
    if isinstance(raw_tags, str):
        try:
            parsed = json.loads(raw_tags)
            tags = parsed if isinstance(parsed, list) else raw_tags.split(",")
        except (TypeError, ValueError, json.JSONDecodeError):
            tags = raw_tags.split(",")
    elif isinstance(raw_tags, list):
        tags = raw_tags
    else:
        tags = []

    cleaned = []

    for tag in tags:
        normalized = re.sub(r"\s+", " ", str(tag).strip().lower())

        if normalized and normalized not in cleaned:
            cleaned.append(normalized)

    return cleaned[:8]


class ScoutIntelligence:
    def __init__(self):
        self.ai = MapleAIEngine()

    def analyze_article(self, article, matched_anime=None):
        if getattr(article, "intelligence_category", None):
            return {
                "category": article.intelligence_category,
                "importance": article.intelligence_importance,
                "confidence": getattr(article, "intelligence_confidence", None),
                "event": article.intelligence_event,
                "anime": article.intelligence_anime,
                "summary": article.intelligence_summary,
                "tags": getattr(article, "intelligence_tags", None),
            }

        matched_title = getattr(matched_anime, "title", "") if matched_anime else ""
        categories = " | ".join(category.value for category in ScoutCategory)
        prompt = f"""
You are Scout, an anime news intelligence system.

Analyze this anime news article and return ONLY valid JSON.

Article Title:
{article.title}

Article Summary:
{article.summary or ""}

Known Anime Match:
{matched_title or "None"}

JSON shape:
{{
  "category": "{categories}",
  "importance": 0,
  "confidence": 0,
  "event": "",
  "anime": "",
  "summary": "",
  "tags": []
}}

Rules:
- Return ONLY valid JSON.
- category must be one of the exact category strings listed above.
- confidence must be 0-100.
- importance must be 0-100.
- Only use confidence 90+ when you are very confident.
- event should name the underlying story, not the publishing outlet.
- Use the Known Anime Match when it fits the article.
- summary must be under 40 words.
- tags must contain 3-8 lowercase strings.
- Always include the anime title as a lowercase tag when known.
- Include event tags like "season 2", "trailer", "english dub", "simuldub", "voice cast", "movie", or "release date" when relevant.
- Include genre/theme tags when obvious, such as "fantasy", "romance", "action", "isekai", "medical mystery", or "historical".
- If the article or post mentions English dub, dub cast, simuldub, dubbed premiere, or home video dub release, use one of the dub categories.
- Do not include markdown.
- Do not include explanation outside JSON.
""".strip()

        try:
            raw = self.ai.answer(prompt)
            intel = _extract_json(raw)
        except Exception:
            return {
                "category": ScoutCategory.GENERAL.value,
                "importance": 50,
                "confidence": 30,
                "event": "Unknown",
                "anime": matched_title,
                "summary": article.summary or article.title,
                "tags": _normalize_tags(
                    [matched_title.lower(), "general news"] if matched_title else ["general news"]
                ),
            }

        category = normalize_category(
            intel.get("category") or classify_article(article.title, article.summary)
        )
        confidence = clamp_score(intel.get("confidence"), default=55)
        article_text = f"{article.title or ''} {article.summary or ''}"
        studio = getattr(matched_anime, "studio", None) if matched_anime else None
        anime_title = intel.get("anime") or matched_title

        return {
            "category": category.value,
            "importance": calculate_importance(
                category,
                ai_importance=intel.get("importance"),
                confidence=confidence,
                article_text=article_text,
                studio=studio,
            ),
            "confidence": confidence,
            "event": intel.get("event") or "Unknown",
            "anime": anime_title,
            "summary": intel.get("summary") or article.summary or article.title,
            "tags": _normalize_tags(intel.get("tags")),
        }
