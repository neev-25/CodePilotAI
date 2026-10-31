import logging
import time
from collections.abc import Callable
from datetime import datetime, timedelta
from math import ceil

from sqlalchemy import func, text

from app.core.config import settings
from app.database.database import SessionLocal, engine
from app.models.embedding_rate_reservation import EmbeddingRateReservation

WINDOW = timedelta(minutes=1)
ADVISORY_LOCK_KEY = 718392641
logger = logging.getLogger(__name__)


class EmbeddingConfigurationError(ValueError):
    """Raised when a configured batch cannot fit inside the token budget."""


def estimate_tokens(text_value: str) -> int:
    """Conservative rough estimate; actual Gemini tokenization can differ."""
    return max(1, ceil(len(text_value) / 3))


class EmbeddingRateLimiter:
    """Database-coordinated rolling token budget shared by application workers."""

    def reserve(
        self,
        token_count: int,
        *,
        progress: Callable[[dict], None] | None = None,
        repository_id: int | None = None,
        job_id: int | None = None,
    ) -> float:
        budget = settings.EMBEDDING_TOKENS_PER_MINUTE
        if token_count > budget:
            raise EmbeddingConfigurationError(
                f"Embedding batch estimate ({token_count}) exceeds the configured "
                f"per-minute token budget ({budget}). Reduce the batch size or "
                "increase EMBEDDING_TOKENS_PER_MINUTE to match your actual quota."
            )
        if engine.dialect.name != "postgresql":
            raise RuntimeError(
                "Shared embedding rate limiting requires PostgreSQL. "
                "Configure DATABASE_URL for PostgreSQL or Neon."
            )

        while True:
            db = SessionLocal()
            wait_seconds = 0.0
            try:
                with db.begin():
                    db.execute(
                        text("SELECT pg_advisory_xact_lock(:lock_key)"),
                        {"lock_key": ADVISORY_LOCK_KEY},
                    )
                    now = datetime.utcnow()
                    window_start = now - WINDOW
                    db.query(EmbeddingRateReservation).filter(
                        EmbeddingRateReservation.reserved_at < window_start
                    ).delete(synchronize_session=False)

                    used_tokens = (
                        db.query(
                            func.coalesce(
                                func.sum(EmbeddingRateReservation.estimated_tokens),
                                0,
                            )
                        )
                        .filter(
                            EmbeddingRateReservation.reserved_at >= window_start
                        )
                        .scalar()
                    )
                    if used_tokens + token_count <= budget:
                        db.add(
                            EmbeddingRateReservation(
                                estimated_tokens=token_count,
                                reserved_at=now,
                            )
                        )
                    else:
                        oldest_reservation = (
                            db.query(
                                func.min(EmbeddingRateReservation.reserved_at)
                            )
                            .filter(
                                EmbeddingRateReservation.reserved_at >= window_start
                            )
                            .scalar()
                        )
                        if oldest_reservation is not None:
                            wait_seconds = max(
                                0.1,
                                (oldest_reservation + WINDOW - now).total_seconds(),
                            )
            finally:
                db.close()

            if wait_seconds == 0:
                return 0.0
            logger.info(
                "Embedding token budget reached: repository_id=%s job_id=%s "
                "estimated_tokens=%s wait_seconds=%.2f",
                repository_id,
                job_id,
                token_count,
                wait_seconds,
            )
            if progress:
                progress(
                    {
                        "state": "waiting_for_quota",
                        "estimated_tokens": token_count,
                        "wait_seconds": wait_seconds,
                        "message": (
                            "Waiting for the shared Gemini embedding token budget "
                            f"({wait_seconds:.0f} seconds)."
                        ),
                    }
                )
            time.sleep(wait_seconds)


rate_limiter = EmbeddingRateLimiter()
