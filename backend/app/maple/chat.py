from app.maple.ai_core import ask_maple_ai
from app.maple.explanations import generate_explanation
from app.maple.memory import update_user_memory
from app.maple.personalization import get_personalized_recommendations
from app.maple.recommendations import get_similar_anime
from app.maple.trends import get_trending_anime


def build_chat_context(
    message: str,
    anime_id: int | None = None,
    user_id: str = "guest",
):
    msg = message.lower()
    user_memory = update_user_memory(user_id, message, anime_id)

    context = {
        "user_memory": user_memory,
    }

    if anime_id:
        context["anime_id"] = anime_id
        context["similar"] = get_similar_anime(anime_id, limit=5)
        context["explanation"] = generate_explanation(anime_id)

    if any(word in msg for word in ["trend", "popular", "recommend", "suggest", "watch"]):
        context["trending"] = get_trending_anime(limit=5)

    if any(word in msg for word in ["recommend", "suggest", "watch"]):
        context["personalized"] = get_personalized_recommendations(
            ["action", "fantasy"], limit=5
        )

    return context


def chat_maple(
    message: str,
    anime_id: int | None = None,
    user_id: str = "guest",
):
    # -------------------------
    # BUILD CONTEXT
    # -------------------------
    context = build_chat_context(message, anime_id, user_id)

    # -------------------------
    # AI RESPONSE
    # -------------------------
    reply = ask_maple_ai(message, context)

    return {
        "type": "ai",
        "response": reply,
        "context_used": bool(context),
        "memory_used": True,
    }
