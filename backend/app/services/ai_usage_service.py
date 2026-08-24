import hashlib
from sqlalchemy.orm import Session
from app.models.ai_usage_log import AIUsageLog


class AIUsageService:
    """Records every LLM call for analytics purposes."""

    @staticmethod
    def log(db: Session, repository_id: int, service_name: str, prompt: str) -> None:
        input_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        estimated_tokens = max(1, len(prompt) // 4)
        db.add(AIUsageLog(
            repository_id=repository_id,
            service_name=service_name,
            input_hash=input_hash,
            estimated_tokens=estimated_tokens,
        ))
        db.commit()
