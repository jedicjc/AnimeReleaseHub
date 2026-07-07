import os
from openai import OpenAI


class MapleAIEngine:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def answer(self, prompt: str) -> str:
        response = self.client.responses.create(
            model="gpt-5-mini",
            input=prompt,
            max_output_tokens=1000,
        )

        answer = response.output_text.strip()

        if not answer:
            status = getattr(response, "status", "unknown")
            incomplete_details = getattr(response, "incomplete_details", None)

            raise RuntimeError(
                "OpenAI returned an empty answer "
                f"(status={status}, incomplete_details={incomplete_details})"
            )

        return answer
