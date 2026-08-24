from app.worker.celery_app import celery_app
from app.services.indexing_job_service import IndexingJobService


@celery_app.task(
    name="codepilot.index_repository",
    bind=True,
    max_retries=2,
    default_retry_delay=60,
)
def index_repository_task(self, job_id: int, repository_id: int) -> None:
    """
    Celery task wrapper around IndexingJobService.run.
    Retries up to 2 times on unexpected exceptions.
    """
    try:
        IndexingJobService.run(job_id, repository_id)
    except Exception as exc:
        raise self.retry(exc=exc)
