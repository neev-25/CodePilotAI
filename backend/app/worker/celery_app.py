from celery import Celery

REDIS_URL = "redis://localhost:6379/0"

celery_app = Celery(
    "codepilot",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Retry failed tasks once after 60 s
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
