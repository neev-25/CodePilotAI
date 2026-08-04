# from google import genai

# from app.core.config import settings


# class GeminiClient:

#     def __init__(self):
#         self.client = genai.Client(
#             api_key=settings.GEMINI_API_KEY
#         )

#     def generate(self, prompt: str) -> str:

#         response = self.client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=prompt,
#         )

#         return response.text

import json
import re
import time

from google import genai
from google.genai.errors import APIError

from app.core.config import settings


class GeminiClient:

    MAX_RETRIES = 3
    RETRY_DELAY = 3

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def generate(self, prompt: str) -> str:

        last_error = None

        for attempt in range(self.MAX_RETRIES):

            try:

                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )

                if not response.text:
                    raise Exception("Gemini returned an empty response.")

                return response.text.strip()

            except APIError as e:

                last_error = e

                # Retry on temporary overload
                if e.code in (429, 500, 503):

                    print(
                        f"Gemini unavailable (attempt {attempt+1}/{self.MAX_RETRIES}), retrying..."
                    )

                    time.sleep(self.RETRY_DELAY)

                    continue

                raise

        raise last_error

    def generate_json(self, prompt: str):

        response = self.generate(prompt)

        response = response.strip()

        # Remove markdown fences
        response = re.sub(
            r"^```json",
            "",
            response,
            flags=re.IGNORECASE,
        )

        response = re.sub(
            r"^```",
            "",
            response,
        )

        response = re.sub(
            r"```$",
            "",
            response,
        )

        response = response.strip()

        start = response.find("{")
        end = response.rfind("}")

        if start == -1 or end == -1:

            print(response)

            raise Exception("Gemini did not return JSON.")

        response = response[start:end + 1]

        try:

            return json.loads(response)

        except json.JSONDecodeError:

            print(response)

            raise Exception("Gemini returned invalid JSON.")