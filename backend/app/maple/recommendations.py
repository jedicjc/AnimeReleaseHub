from app.database.connection import SessionLocal
from app.database.models import Anime


def calculate_similarity(target, candidate):
    score = 0
    reasons = []

    target_genres = set((target.genres or "").lower().split(","))
    candidate_genres = set((candidate.genres or "").lower().split(","))

    # --------------------------
    # GENRE MATCH (STRONG SIGNAL)
    # --------------------------
    common_genres = target_genres.intersection(candidate_genres)

    if common_genres:
        score += len(common_genres) * 15
        reasons.append(f"Shared genres: {', '.join(common_genres)}")

    # --------------------------
    # SCORE SIMILARITY
    # --------------------------
    if target.score and candidate.score:
        diff = abs(target.score - candidate.score)

        if diff < 0.5:
            score += 20
            reasons.append("Very similar ratings")
        elif diff < 1.5:
            score += 10
            reasons.append("Similar ratings")

    # --------------------------
    # STATUS ALIGNMENT
    # --------------------------
    if target.status == candidate.status:
        score += 8
        reasons.append("Same release status")

    # --------------------------
    # POPULARITY BOOST
    # --------------------------
    if candidate.score and candidate.score >= 8:
        score += 5
        reasons.append("Highly rated title")

    return score, reasons


def get_similar_anime(anime_id: int, limit: int = 6):
    db = SessionLocal()

    try:
        target = db.query(Anime).filter(Anime.id == anime_id).first()

        if not target:
            return []

        all_anime = db.query(Anime).all()

        results = []

        for a in all_anime:
            if a.id == anime_id:
                continue

            score, reasons = calculate_similarity(target, a)

            if score <= 0:
                continue

            results.append({
                "id": a.id,
                "title": a.title,
                "poster_url": a.poster_url,
                "score": round(score, 2),
                "why": reasons[:3],  # keep UI clean
            })

        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:limit]

    finally:
        db.close()