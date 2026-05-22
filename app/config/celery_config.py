import os
from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL")

celery = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery.conf.update(
    task_track_started=True,
    result_expires=3600,
)

celery.conf.beat_schedule = {
    "clean-temp-files-daily": {
        "task": "tasks.delete_old_files",
        "schedule": crontab(hour=2, minute=0),
    },
}

celery.conf.timezone = "UTC" # type: ignore