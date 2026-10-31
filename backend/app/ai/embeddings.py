import logging
import random
import re
import time
from collections.abc import Callable, Iterator, Sequence

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.ai.embedding_rate_limiter import (
    estimate_tokens,
    rate_limiter,
)
from app.core.config import settings

logger = logging.getLogger(__name__)
ProgressCallback = Callable[[dict], None]


def _error_details(error: Exception) -> tuple[bool, float | None]:
    """Return whether an exception is transient and any Google retry delay."""
    messages = []
    current: BaseException | None = error
    status_codes = set()
    while current is not None:
        messages.append(str(current))
        status_code = getattr(current, "status_code", getattr(current, "code", None))
        if status_code is not None:
            status_codes.add(str(status_code))
        if isinstance(current, (TimeoutError, ConnectionError, OSError)):
            return True, None
        current = current.__cause__ or current.__context__

    details = " ".join(messages).lower()
    retry_match = re.search(
        r"retrydelay['\"]?\s*:\s*['\"]?(\d+(?:\.\d+)?)\s*(ms|s|m)",
        details,
        re.IGNORECASE,
    )
    retry_delay = None
    if retry_match:
        value = float(retry_match.group(1))
        unit = retry_match.group(2)
        retry_delay = value / 1000 if unit == "ms" else value * (60 if unit == "m" else 1)

    transient = (
        any(code in {"408", "429", "500", "502", "503", "504"} for code in status_codes)
        or isinstance(error, (TimeoutError, ConnectionError, OSError))
        or any(
            marker in details
            for marker in (
                "429",
                "resource_exhausted",
                "500 internal",
                "502",
                "503",
                "504",
                "timeout",
                "timed out",
                "connection reset",
                "connection aborted",
                "connection refused",
                "network is unreachable",
                "temporarily unavailable",
            )
        )
    )
    return transient, retry_delay


class EmbeddingQuotaError(RuntimeError):
    """Raised when transient embedding failures persist after bounded retries."""


class EmbeddingModel:
    """Batched Gemini embeddings with shared quota coordination and bounded retries."""

    def __init__(self) -> None:
        self.batch_size = settings.EMBEDDING_BATCH_SIZE
        self.model = GoogleGenerativeAIEmbeddings(
            model=settings.GEMINI_EMBEDDING_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
        )

    def iter_encode(
        self,
        texts: Sequence[str],
        *,
        repository_id: int | None = None,
        job_id: int | None = None,
        progress: ProgressCallback | None = None,
    ) -> Iterator[tuple[int, int, list[list[float]], int]]:
        """Embed in bounded batches, yielding each completed batch in input order."""
        batch_size = settings.EMBEDDING_BATCH_SIZE
        total_batches = (len(texts) + batch_size - 1) // batch_size
        for batch_index, offset in enumerate(range(0, len(texts), batch_size), start=1):
            batch = list(texts[offset : offset + batch_size])
            tokens = sum(estimate_tokens(item) for item in batch)
            for attempt in range(settings.EMBEDDING_MAX_RETRIES + 1):
                try:
                    rate_limiter.reserve(
                        tokens,
                        progress=progress,
                        repository_id=repository_id,
                        job_id=job_id,
                    )
                    vectors = self.model.embed_documents(batch)
                    if len(vectors) != len(batch):
                        raise RuntimeError(
                            "Gemini returned a different number of embeddings than inputs."
                        )
                    break
                except Exception as error:
                    transient, retry_delay = _error_details(error)
                    if not transient or attempt >= settings.EMBEDDING_MAX_RETRIES:
                        if transient:
                            logger.error(
                                "Embedding batch retries exhausted: repository_id=%s "
                                "job_id=%s batch=%s/%s tokens=%s",
                                repository_id,
                                job_id,
                                batch_index,
                                total_batches,
                                tokens,
                            )
                            raise EmbeddingQuotaError(
                                "Gemini embedding quota or service remained unavailable "
                                f"after {settings.EMBEDDING_MAX_RETRIES} retries. "
                                "Wait for the quota window to reset, then retry indexing; "
                                "completed batches will be reused."
                            ) from error
                        raise

                    backoff = min(
                        settings.EMBEDDING_MAX_BACKOFF,
                        settings.EMBEDDING_INITIAL_BACKOFF * (2**attempt),
                    )
                    delay = retry_delay if retry_delay is not None else (
                        backoff * random.uniform(0.75, 1.25)
                    )
                    logger.warning(
                        "Embedding request retry: repository_id=%s job_id=%s "
                        "batch=%s/%s retry=%s/%s tokens=%s wait_seconds=%.2f error=%s",
                        repository_id,
                        job_id,
                        batch_index,
                        total_batches,
                        attempt + 1,
                        settings.EMBEDDING_MAX_RETRIES,
                        tokens,
                        delay,
                        error,
                    )
                    if progress:
                        progress(
                            {
                                "state": "retrying",
                                "current_batch": batch_index,
                                "total_batches": total_batches,
                                "retry_attempt": attempt + 1,
                                "retry_limit": settings.EMBEDDING_MAX_RETRIES,
                                "estimated_tokens": tokens,
                                "message": (
                                    "Embedding quota or service limit reached; "
                                    f"retrying in {delay:.0f} seconds."
                                ),
                            }
                        )
                    time.sleep(delay)

            yield batch_index, total_batches, vectors, tokens
            if settings.EMBEDDING_BATCH_DELAY and batch_index < total_batches:
                time.sleep(settings.EMBEDDING_BATCH_DELAY)

    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        """Return all vectors in input order; callers needing resume should stream."""
        return [
            vector
            for _, _, batch_vectors, _ in self.iter_encode(texts)
            for vector in batch_vectors
        ]

    def embed_query(self, text: str) -> list[float]:
        tokens = estimate_tokens(text)
        for attempt in range(settings.EMBEDDING_MAX_RETRIES + 1):
            try:
                rate_limiter.reserve(tokens)
                return self.model.embed_query(text)
            except Exception as error:
                transient, retry_delay = _error_details(error)
                if not transient or attempt >= settings.EMBEDDING_MAX_RETRIES:
                    if transient:
                        raise EmbeddingQuotaError(
                            "Gemini embedding quota or service remained unavailable "
                            f"after {settings.EMBEDDING_MAX_RETRIES} retries."
                        ) from error
                    raise
                backoff = min(
                    settings.EMBEDDING_MAX_BACKOFF,
                    settings.EMBEDDING_INITIAL_BACKOFF * (2**attempt),
                )
                delay = retry_delay if retry_delay is not None else (
                    backoff * random.uniform(0.75, 1.25)
                )
                logger.warning(
                    "Embedding query retry=%s/%s tokens=%s wait_seconds=%.2f error=%s",
                    attempt + 1,
                    settings.EMBEDDING_MAX_RETRIES,
                    tokens,
                    delay,
                    error,
                )
                time.sleep(delay)
        raise RuntimeError("Embedding query retry loop exited unexpectedly.")
