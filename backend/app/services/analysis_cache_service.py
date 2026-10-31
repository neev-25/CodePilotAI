import json
from collections.abc import Callable
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.analysis_cache import AnalysisCache


class AnalysisCacheService:
    """Caches completed AI results so revisiting a page never spends another model call."""

    @staticmethod
    def get_or_generate(
        db: Session,
        repository_id: int,
        artifact_type: str,
        generate: Callable[[], Any],
        inputs: dict[str, Any] | None = None,
    ) -> Any:
        input_key = json.dumps(inputs or {}, sort_keys=True, separators=(",", ":"))
        cached = (
            db.query(AnalysisCache)
            .filter(
                AnalysisCache.repository_id == repository_id,
                AnalysisCache.artifact_type == artifact_type,
                AnalysisCache.input_key == input_key,
            )
            .first()
        )
        if cached:
            return json.loads(cached.payload)

        result = jsonable_encoder(generate())
        db.add(
            AnalysisCache(
                repository_id=repository_id,
                artifact_type=artifact_type,
                input_key=input_key,
                payload=json.dumps(result),
            )
        )
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
        return result

    @staticmethod
    def invalidate_repository(db: Session, repository_id: int) -> None:
        db.query(AnalysisCache).filter(AnalysisCache.repository_id == repository_id).delete()
        db.commit()
