import json
import logging
import traceback

from app.core.config import settings


class _JsonFormatter(logging.Formatter):
    """Emit one JSON object per log record — parseable by Datadog, GCP, etc."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def _build_logger() -> logging.Logger:
    handler = logging.StreamHandler()

    if settings.ENVIRONMENT == "production":
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # Avoid adding duplicate handlers on repeated imports
    if not root.handlers:
        root.addHandler(handler)
    else:
        root.handlers[0] = handler

    return logging.getLogger("codepilot")


logger = _build_logger()