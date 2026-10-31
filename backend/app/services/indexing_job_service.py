import json
from datetime import datetime
import time

from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.indexing_job import IndexingJob
from app.models.repository import Repository
from app.services.indexing_service import IndexingService
from app.services.analysis_cache_service import AnalysisCacheService
from app.ai.embeddings import EmbeddingQuotaError
from app.ai.embedding_rate_limiter import EmbeddingConfigurationError
from app.core.logger import logger


class IndexingJobService:
    @staticmethod
    def _close_session(db: Session) -> None:
        try:
            db.close()
        except SQLAlchemyError:
            logger.warning("Could not cleanly close an indexing database session.", exc_info=True)

    @staticmethod
    def _invalidate_cache(repository_id: int) -> None:
        for attempt in range(3):
            db: Session = SessionLocal()
            try:
                AnalysisCacheService.invalidate_repository(db, repository_id)
                return
            except OperationalError:
                try:
                    db.rollback()
                except SQLAlchemyError:
                    logger.warning(
                        "Could not roll back cache invalidation session.",
                        exc_info=True,
                    )
                if attempt == 2:
                    raise
                delay = 2**attempt
                logger.warning(
                    "Database connection failed while invalidating repository cache; "
                    "retrying repository_id=%s attempt=%s/3 wait_seconds=%s",
                    repository_id,
                    attempt + 1,
                    delay,
                )
                time.sleep(delay)
            finally:
                IndexingJobService._close_session(db)

    @staticmethod
    def update_progress(job_id: int, progress: dict) -> None:
        db: Session = SessionLocal()
        try:
            job = db.get(IndexingJob, job_id)
            if not job:
                logger.warning("Cannot update progress for missing indexing job %s.", job_id)
                return
            state = progress.get("state")
            job.status = "RETRYING" if state in {"retrying", "waiting_for_quota"} else "RUNNING"
            job.message = progress.get("message", "Indexing repository.")
            job.result_json = json.dumps(progress)
            db.commit()
        finally:
            IndexingJobService._close_session(db)

    @staticmethod
    def run(job_id: int, repository_id: int) -> None:
        db: Session = SessionLocal()
        try:
            job = db.get(IndexingJob, job_id)
            repo = db.get(Repository, repository_id)
            if not job or not repo:
                logger.warning(
                    "Skipping indexing job %s because job or repository %s is missing.",
                    job_id,
                    repository_id,
                )
                return
            repository_path = repo.local_path
            job.status = "RUNNING"
            job.message = "Scanning repository files."
            db.commit()
        finally:
            IndexingJobService._close_session(db)

        try:
            result = IndexingService.index(
                repository_id,
                repository_path,
                job_id=job_id,
                progress=lambda progress: IndexingJobService.update_progress(
                    job_id,
                    progress,
                ),
            )
            IndexingJobService._invalidate_cache(repository_id)

            db = SessionLocal()
            try:
                job = db.get(IndexingJob, job_id)
                repo = db.get(Repository, repository_id)
                if not job or not repo:
                    logger.warning(
                        "Could not finalize indexing job %s because job or repository %s disappeared.",
                        job_id,
                        repository_id,
                    )
                    return
                repo.status = "INDEXED"
                job.status = "COMPLETED"
                job.message = "Repository indexed successfully."
                job.result_json = json.dumps({"state": "completed", **result})
                job.completed_at = datetime.utcnow()
                db.commit()
            finally:
                IndexingJobService._close_session(db)
        except Exception as error:
            logger.exception("Indexing job %s failed.", job_id)
            db = SessionLocal()
            try:
                job = db.get(IndexingJob, job_id)
                repo = db.get(Repository, repository_id)
                if repo:
                    repo.status = "FAILED"
                if job:
                    is_quota_error = isinstance(error, EmbeddingQuotaError)
                    is_config_error = isinstance(error, EmbeddingConfigurationError)
                    job.status = "PAUSED" if is_quota_error else "FAILED"
                    job.message = (
                        str(error)
                        if is_quota_error or is_config_error
                        else "Indexing failed. Check backend logs and retry the job."
                    )
                    previous_progress = {}
                    if job.result_json:
                        try:
                            previous_progress = json.loads(job.result_json)
                        except json.JSONDecodeError:
                            logger.warning(
                                "Index job %s had invalid progress JSON.",
                                job_id,
                            )
                    job.result_json = json.dumps(
                        {
                            **previous_progress,
                            "state": "paused" if is_quota_error else "failed",
                            "message": job.message,
                        }
                    )
                    job.completed_at = datetime.utcnow()
                db.commit()
            except Exception:
                try:
                    db.rollback()
                except SQLAlchemyError:
                    logger.warning(
                        "Could not roll back while saving failed indexing status.",
                        exc_info=True,
                    )
                logger.exception(
                    "Could not save final status for indexing job %s after its failure.",
                    job_id,
                )
            finally:
                IndexingJobService._close_session(db)
