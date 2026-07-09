from dataclasses import dataclass, field


@dataclass
class ScoutEvent:
    anime: str
    event: str
    category: str
    importance: int
    confidence: int
    summary: str
    sources: list[str] = field(default_factory=list)
    article_ids: list[int] = field(default_factory=list)


class ScoutEventEngine:
    def build_events(self, articles):
        events = {}

        for article in articles:
            anime = (getattr(article, "intelligence_anime", "") or "").strip()
            event = (getattr(article, "intelligence_event", "") or "").strip()

            if not anime or not event:
                continue

            key = (anime.lower(), event.lower())

            if key not in events:
                events[key] = ScoutEvent(
                    anime=anime,
                    event=event,
                    category=(
                        getattr(article, "intelligence_category", None)
                        or "General News"
                    ),
                    importance=getattr(article, "intelligence_importance", 0) or 0,
                    confidence=getattr(article, "intelligence_confidence", 0) or 0,
                    summary=getattr(article, "intelligence_summary", "") or "",
                )

            source = getattr(article, "source", None)
            if source and source not in events[key].sources:
                events[key].sources.append(source)

            article_id = getattr(article, "id", None)
            if article_id is not None and article_id not in events[key].article_ids:
                events[key].article_ids.append(article_id)

            events[key].importance = max(
                events[key].importance,
                getattr(article, "intelligence_importance", 0) or 0,
            )

            events[key].confidence = max(
                events[key].confidence,
                getattr(article, "intelligence_confidence", 0) or 0,
            )

            if not events[key].summary:
                events[key].summary = (
                    getattr(article, "intelligence_summary", "") or ""
                )

        return sorted(
            events.values(),
            key=lambda event: (event.importance, event.confidence, len(event.sources)),
            reverse=True,
        )
