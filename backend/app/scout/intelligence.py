import json

from app.maple.ai_engine import MapleAIEngine


class ScoutIntelligence:
    def __init__(self):
        self.ai = MapleAIEngine()

    def analyze_article(self, article):
        prompt = f"""
You are Scout, an anime news intelligence system.

Analyze this anime news article and return ONLY valid JSON.

Article Title:
{article.title}

Article Summary:
{article.summary or ""}

JSON shape:
{{
  "category": "Season Announcement | Trailer | New Anime | English Dub | Movie | Casting | Release Date | Manga | Game | Merchandise | General News",
  "importance": 0,
  "event": "",
  "anime": "",
  "summary": ""
}}

Rules:
- importance must be 0-100.
- summary must be under 40 words.
- Do not include markdown.
- Do not include explanation outside JSON.
""".strip()

        try:
            raw = self.ai.answer(prompt)
            return json.loads(raw)
        except Exception:
            return {
                "category": "General News",
                "importance": 50,
                "event": "Unknown",
                "anime": "",
                "summary": article.summary or article.title,
            }
