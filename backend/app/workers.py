from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass


@dataclass(slots=True)
class WorkerState:
    name: str
    healthy: bool = True
    reconnecting: bool = False


class WorkerPool:
    def __init__(self, worker_names: list[str]):
        self._workers = deque(WorkerState(name=name) for name in worker_names)
        self._lock = asyncio.Lock()

    async def next_worker(self) -> WorkerState:
        async with self._lock:
            self._workers.rotate(-1)
            return self._workers[0]

    async def mark_unhealthy(self, worker_name: str) -> None:
        async with self._lock:
            for worker in self._workers:
                if worker.name == worker_name:
                    worker.healthy = False
                    worker.reconnecting = True

    async def reconnect(self, worker_name: str) -> None:
        async with self._lock:
            for worker in self._workers:
                if worker.name == worker_name:
                    worker.healthy = True
                    worker.reconnecting = False

    async def status(self) -> list[dict[str, str | bool]]:
        async with self._lock:
            return [
                {"name": w.name, "healthy": w.healthy, "reconnecting": w.reconnecting}
                for w in self._workers
            ]


worker_pool = WorkerPool(["worker1", "worker2", "worker3", "worker4", "worker5"])
