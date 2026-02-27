from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery("synaptic_hive", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    include=["app.workers.anomaly_task"],
    beat_schedule={
        "detect-anomalies-hourly": {
            "task": "anomaly.detect_all",
            "schedule": crontab(minute=0),
        },
    },
)
