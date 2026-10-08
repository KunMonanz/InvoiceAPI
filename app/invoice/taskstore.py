import threading
from typing import Any

_tasks_lock = threading.Lock()
TASK_STORE: dict[str, dict[str, Any]] = {}


def update_task_state(task_id: str, state: str, result: Any = None):
    with _tasks_lock:
        TASK_STORE[task_id] = {"state": state, "result": result}


def get_task_state(task_id: str) -> dict[str, Any] | None:
    with _tasks_lock:
        return TASK_STORE.get(task_id)
