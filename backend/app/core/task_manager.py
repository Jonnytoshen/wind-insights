from __future__ import annotations

import asyncio
import threading
import time
import uuid
from dataclasses import dataclass, field


@dataclass
class TaskState:
    task_id: str
    status: str = "pending"   # pending | running | success | error
    progress: int = 0
    message: str = ""
    current_step: str = ""
    result: dict | None = None
    created_at: float = field(default_factory=time.time)
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)

    def to_progress_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "current_step": self.current_step,
        }


class TaskManager:
    def __init__(self, timeout_seconds: int = 300) -> None:
        self._tasks: dict[str, TaskState] = {}
        self._lock = threading.Lock()
        self._timeout = timeout_seconds

    def create_task(self) -> TaskState:
        task_id = str(uuid.uuid4())
        state = TaskState(task_id=task_id)
        with self._lock:
            self._prune_expired()
            self._tasks[task_id] = state
        return state

    def get_task(self, task_id: str) -> TaskState | None:
        with self._lock:
            return self._tasks.get(task_id)

    def update_task(
        self,
        task_id: str,
        *,
        status: str | None = None,
        progress: int | None = None,
        message: str | None = None,
        current_step: str | None = None,
        result: dict | None = None,
    ) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return
            if status is not None:
                task.status = status
            if progress is not None:
                task.progress = progress
            if message is not None:
                task.message = message
            if current_step is not None:
                task.current_step = current_step
            if result is not None:
                task.result = result
        # Push progress to SSE queue (outside lock to avoid deadlock)
        if task is not None:
            asyncio.get_event_loop().call_soon_threadsafe(
                task.queue.put_nowait, task.to_progress_dict()
            )

    def _prune_expired(self) -> None:
        """Remove tasks older than 2× timeout to prevent unbounded memory growth."""
        cutoff = time.time() - self._timeout * 2
        expired = [tid for tid, t in self._tasks.items() if t.created_at < cutoff]
        for tid in expired:
            del self._tasks[tid]


# Singleton instance, imported by routers and services
task_manager = TaskManager()
