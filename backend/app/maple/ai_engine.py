import os

from openai import OpenAI


class MapleAIEngine:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        self.client = OpenAI(api_key=api_key)

    def answer(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=os.getenv("MAPLE_OPENAI_MODEL", "gpt-5-mini"),
            input=prompt,
            max_output_tokens=300,
        )

        return response.output_text.strip()
