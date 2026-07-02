import os
import time
from pathlib import Path

from openai import OpenAI


SYSTEM_PROMPT = """
You are Maple, an anime intelligence assistant.

You help users:
- find trending anime
- recommend anime
- explain why anime is popular
- compare anime
- give insights based on structured anime data

Be concise, helpful, and analytical.
"""
FALLBACK_RESPONSE = "Maple is temporarily unavailable. Try again soon."


def safe_call(fn, retries=2):
    for _ in range(retries):
        try:
            return fn()
        except Exception as e:
            print("MAPLE ERROR:", str(e))
            time.sleep(1)

    return None


def load_backend_env():
    env_path = Path(__file__).resolve().parents[2] / ".env"

    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


def get_client():
    load_backend_env()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing in environment")

    if api_key in {"your_key_here", "your_real_key_here"}:
        raise RuntimeError("OPENAI_API_KEY is still using a placeholder value")

    return OpenAI(api_key=api_key)


def ask_maple_ai(user_message: str, context: dict | None = None):
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        if context:
            messages.append(
                {
                    "role": "system",
                    "content": f"Context data: {context}",
                }
            )

        messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        response = safe_call(
            lambda: get_client().chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.4,
            )
        )

        if response is None:
            return FALLBACK_RESPONSE

        return response.choices[0].message.content
    except Exception as e:
        print("MAPLE ERROR:", str(e))
        return FALLBACK_RESPONSE


def ask_maple_ai_stream(user_message: str, context: dict | None = None):
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        if context:
            messages.append(
                {
                    "role": "system",
                    "content": f"Context data: {context}",
                }
            )

        messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        stream = safe_call(
            lambda: get_client().chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.4,
                stream=True,
            )
        )

        if stream is None:
            yield FALLBACK_RESPONSE
            return

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        print("MAPLE ERROR:", str(e))
        yield FALLBACK_RESPONSE
