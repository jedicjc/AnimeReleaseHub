import json
from pathlib import Path


MEMORY_FILE = Path(__file__).resolve().parents[2] / "maple_memory.json"
DEFAULT_MEMORY = {
    "genres": [],
    "liked_anime": [],
    "queries": [],
}


def load_memory():
    if not MEMORY_FILE.exists():
        return {}

    with MEMORY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(memory):
    with MEMORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def get_user_memory(user_id: str):
    memory = load_memory()
    return memory.get(user_id, DEFAULT_MEMORY.copy())


def update_user_memory(user_id: str, message: str, anime_id=None):
    memory = load_memory()

    if user_id not in memory:
        memory[user_id] = DEFAULT_MEMORY.copy()

    user_memory = memory[user_id]

    # Store query history.
    user_memory["queries"].append(message)

    # Simple heuristic learning.
    msg = message.lower()

    if "action" in msg:
        user_memory["genres"].append("action")
    if "fantasy" in msg:
        user_memory["genres"].append("fantasy")
    if "romance" in msg:
        user_memory["genres"].append("romance")

    if anime_id:
        user_memory["liked_anime"].append(anime_id)

    user_memory["genres"] = list(dict.fromkeys(user_memory["genres"]))
    user_memory["liked_anime"] = list(dict.fromkeys(user_memory["liked_anime"]))
    user_memory["queries"] = user_memory["queries"][-50:]

    save_memory(memory)

    return user_memory
