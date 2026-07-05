def join_names(items):
    if not items:
        return ""

    return ", ".join(
        item.get("name", "")
        for item in items
        if item.get("name")
    )


class ScoutNormalizer:
    def normalize_jikan_anime(self, item):
        images = item.get("images") or {}
        jpg = images.get("jpg") or {}
        trailer = item.get("trailer") or {}

        return {
            "mal_id": item.get("mal_id"),
            "title": item.get("title"),
            "title_english": item.get("title_english"),
            "title_japanese": item.get("title_japanese"),
            "type": item.get("type"),
            "episodes": item.get("episodes"),
            "status": item.get("status"),
            "season": item.get("season"),
            "year": item.get("year"),
            "synopsis": item.get("synopsis"),
            "rating": item.get("rating"),
            "score": item.get("score"),
            "rank": item.get("rank"),
            "popularity": item.get("popularity"),
            "members": item.get("members"),
            "favorites": item.get("favorites"),
            "genres": join_names(item.get("genres")),
            "themes": join_names(item.get("themes")),
            "demographics": join_names(item.get("demographics")),
            "studios": join_names(item.get("studios")),
            "image_url": jpg.get("large_image_url") or jpg.get("image_url"),
            "trailer_url": trailer.get("url"),
        }

    def normalize_news(self, item):
        return {
            "title": item.get("title"),
            "url": item.get("url"),
            "source": item.get("source"),
            "summary": item.get("summary"),
            "published_at": item.get("published_at"),
        }


def normalize_jikan_anime(item):
    return ScoutNormalizer().normalize_jikan_anime(item)
