import os
import sys
from pathlib import Path

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

# 1. Resolve exact directories
current_dir = Path(__file__).resolve().parent  # app/config
app_dir = current_dir.parent  # app
project_root = app_dir.parent  # InvoiceAPI (Project Root)

# 2. FIX: Inject the project root and app folders into Python's search path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# 3. Load .env environment variables
load_dotenv(dotenv_path=project_root / ".env")

# 4. Dynamic Task Discovery
task_modules = []
for p in app_dir.rglob("*.py"):
    if "task" in p.name and not p.name.startswith("__"):
        relative_path = p.relative_to(project_root)
        module_path = ".".join(relative_path.with_suffix("").parts)
        task_modules.append(module_path)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")

celery = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=task_modules,
)

celery.conf.update(
    task_track_started=True,
    result_expires=3600,
    timezone="UTC",
)

celery.conf.beat_schedule = {
    "clean-temp-files-daily": {
        "task": "app.tasks.delete_saved_invoices",
        "schedule": crontab(hour=2, minute=0),
    },
}
