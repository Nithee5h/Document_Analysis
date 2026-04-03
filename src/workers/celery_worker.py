from celery import Celery
from src.core.config import settings


celery_app = Celery("document_worker", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task(name="health_check_task")
def health_check_task() -> dict:
    return {"status": "worker_ok"}