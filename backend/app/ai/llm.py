import json
import logging
import re
import time
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiServiceError(RuntimeError):
    """A user-safe failure while communicating with Gemini."""


class GeminiClient:

    MAX_RETRIES = 3
    RETRY_DELAY = 3
    FALLBACK_MODELS = [
        "gemini-3.8-flash",
        "gemini-3.6-flash",
    ]

    def generate(self, prompt: str) -> str:
        return self._generate_text(prompt)

    def _generate_text(
        self,
        prompt: str,
        response_mime_type: str | None = None,
    ) -> str:
        last_error = None

        for model_name in self.FALLBACK_MODELS:
            for attempt in range(self.MAX_RETRIES):
                try:
                    model_options: dict[str, Any] = {
                        "model": model_name,
                        "google_api_key": settings.GEMINI_API_KEY,
                        "max_retries": 0,
                    }
                    if response_mime_type:
                        model_options["response_mime_type"] = response_mime_type

                    response = ChatGoogleGenerativeAI(
                        **model_options
                    ).invoke(prompt)
                    response_text = response.content
                    if isinstance(response_text, list):
                        response_text = "".join(
                            block if isinstance(block, str) else block.get("text", "")
                            for block in response_text
                            if isinstance(block, (str, dict))
                        )

                    if not response_text:
                        raise GeminiServiceError(
                            f"Gemini model {model_name} returned an empty response."
                        )

                    return str(response_text).strip()

                except Exception as error:
                    if isinstance(error, GeminiServiceError):
                        raise
                    last_error = error
                    message = str(error).lower()
                    status_code = getattr(
                        error,
                        "status_code",
                        getattr(error, "code", None),
                    )

                    if (
                        status_code == 429
                        or "resource_exhausted" in message
                        or "quota" in message
                        or "429" in message
                    ):
                        logger.warning(
                            "Gemini model %s quota exhausted; trying the next model.",
                            model_name,
                        )
                        break

                    if status_code == 404 or "not_found" in message or "not found" in message:
                        logger.warning(
                            "Gemini model %s was not found; trying the next model.",
                            model_name,
                        )
                        break

                    if status_code in (500, 503) or any(
                        status in message for status in ("500", "503", "unavailable")
                    ):
                        logger.warning(
                            "Gemini model %s unavailable (attempt %s/%s); retrying.",
                            model_name,
                            attempt + 1,
                            self.MAX_RETRIES,
                        )
                        time.sleep(self.RETRY_DELAY)
                        continue

                    raise GeminiServiceError(
                        f"Gemini request failed using model {model_name}."
                    ) from error

        if last_error:
            raise GeminiServiceError(
                "All configured Gemini models failed or quota limits were reached."
            ) from last_error
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
        response = self._generate_text(
            prompt,
            response_mime_type="application/json",
        )
        try:
            return self._parse_json(response)
        except json.JSONDecodeError:
            repair_prompt = (
                "Return only valid compact JSON. Preserve the meaning and schema of this "
                "malformed JSON; escape all quotes and newlines inside strings.\n\n"
                f"MALFORMED JSON:\n{response}"
            )
            repaired = self._generate_text(
                repair_prompt,
                response_mime_type="application/json",
            )
            try:
                return self._parse_json(repaired)
            except json.JSONDecodeError as error:
                raise GeminiJSONError("Gemini returned malformed JSON after one repair attempt.") from error


class GeminiJSONError(GeminiServiceError):
    """Raised when a model response cannot be made into a valid JSON payload."""


class GeminiService:
    @staticmethod
    def generate_content(prompt: str) -> str:
        return GeminiClient().generate(prompt)
