import os
from celery import Celery

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
