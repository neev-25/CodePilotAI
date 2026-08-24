import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.indexing_job import IndexingJob
from app.models.repository import Repository
from app.services.indexing_service import IndexingService
from app.services.analysis_cache_service import AnalysisCacheService


class IndexingJobService:
    @staticmethod
    def run(job_id: int, repository_id: int) -> None:
        db: Session = SessionLocal()
        try:
            job = db.get(IndexingJob, job_id)
            repo = db.get(Repository, repository_id)
            if not job or not repo:
                return
            job.status = "RUNNING"; job.message = "Scanning and embedding repository files."; db.commit()
            result = IndexingService.index(repo.id, repo.local_path)
            repo.status = "INDEXED"
            job.status = "COMPLETED"; job.message = "Repository indexed successfully."; job.result_json = json.dumps(result); job.completed_at = datetime.utcnow()
            AnalysisCacheService.invalidate_repository(db, repo.id)
            db.commit()
        except Exception as error:
            db.rollback()
            job = db.get(IndexingJob, job_id); repo = db.get(Repository, repository_id)
            if repo: repo.status = "FAILED"
            if job:
                job.status = "FAILED"; job.message = str(error); job.completed_at = datetime.utcnow()
            db.commit()
        finally:
            db.close()
