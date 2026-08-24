import json
import re
import time
from typing import Any

from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.core.config import settings


class GeminiServiceError(RuntimeError):
    """A user-safe failure while communicating with Gemini."""


class GeminiClient:

    MAX_RETRIES = 3
    RETRY_DELAY = 3
    FALLBACK_MODELS = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def generate(self, prompt: str) -> str:
        return self._generate_text(prompt)

    def _generate_text(self, prompt: str, config: types.GenerateContentConfig | None = None) -> str:
        last_error = None

        for model_name in self.FALLBACK_MODELS:
            for attempt in range(self.MAX_RETRIES):
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=config,
                    )

                    if not response.text:
                        raise GeminiServiceError(f"Gemini model {model_name} returned an empty response.")

                    return response.text.strip()

                except APIError as e:
                    last_error = e

                    # Quota / Rate limit (429) or Service Unavailable (500, 503)
                    if e.code == 429 or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower():
                        print(f"Gemini model {model_name} quota exhausted/rate limited. Failing over to next model...")
                        break  # Break retry loop to immediately try next model in FALLBACK_MODELS

                    if e.code in (500, 503):
                        print(
                            f"Gemini model {model_name} unavailable (attempt {attempt+1}/{self.MAX_RETRIES}), retrying..."
                        )
                        time.sleep(self.RETRY_DELAY)
                        continue

                    raise

        if last_error:
            raise GeminiServiceError("All Gemini AI models are temporarily unavailable or quota limited.") from last_error
        raise GeminiServiceError("Gemini did not return a response.")

    @staticmethod
    def _parse_json(text: str) -> Any:
        cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()
        start = min((index for index in (cleaned.find("{"), cleaned.find("[")) if index >= 0), default=-1)
        end = max(cleaned.rfind("}"), cleaned.rfind("]"))
        if start < 0 or end < start:
            raise json.JSONDecodeError("No JSON object or array found", cleaned, 0)
        return json.loads(cleaned[start : end + 1])

    def generate_json(self, prompt: str) -> Any:
        """Generate machine-readable output once, retrying only malformed model output."""
        config = types.GenerateContentConfig(response_mime_type="application/json")
        response = self._generate_text(prompt, config)
        try:
            return self._parse_json(response)
        except json.JSONDecodeError:
            repair_prompt = (
                "Return only valid compact JSON. Preserve the meaning and schema of this "
                "malformed JSON; escape all quotes and newlines inside strings.\n\n"
                f"MALFORMED JSON:\n{response}"
            )
            repaired = self._generate_text(repair_prompt, config)
            try:
                return self._parse_json(repaired)
            except json.JSONDecodeError as error:
                raise GeminiJSONError("Gemini returned malformed JSON after one repair attempt.") from error


class GeminiJSONError(GeminiServiceError):
    """Raised when a model response cannot be made into a valid JSON payload."""
