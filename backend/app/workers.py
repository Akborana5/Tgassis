from __future__ import annotations

import asyncio
import os
import logging
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, RPCError
from .config import settings

logger = logging.getLogger(__name__)

@dataclass
class WorkerState:
    name: str
    client: TelegramClient
    healthy: bool = True
    reconnecting: bool = False

class WorkerPool:
    def __init__(self):
        self._workers: deque[WorkerState] = deque()
        self._lock = asyncio.Lock()
        self._api_id = int(os.getenv("TG_API_ID", "123456"))
        self._api_hash = os.getenv("TG_API_HASH", "dummyhash")

    async def initialize(self):
        sessions_dir = settings.data_dir / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        
        session_files = list(sessions_dir.glob("*.session"))
        if not session_files:
            logger.warning("No session files found. Please add .session files to %s", sessions_dir)
            return

        for sf in session_files:
            name = sf.stem
            client = TelegramClient(str(sf), self._api_id, self._api_hash)
            try:
                await client.connect()
                if not await client.is_user_authorized():
                    logger.warning(f"Session {name} is not authorized.")
                    await client.disconnect()
                    continue
                self._workers.append(WorkerState(name=name, client=client))
                logger.info(f"Worker {name} connected successfully.")
            except Exception as e:
                logger.error(f"Failed to connect worker {name}: {e}")

    async def next_worker(self) -> Optional[WorkerState]:
        async with self._lock:
            healthy_workers = [w for w in self._workers if w.healthy]
            if not healthy_workers:
                return None
            
            # Rotate healthy workers for round-robin
            w = healthy_workers[0]
            self._workers.remove(w)
            self._workers.append(w)
            return w

    async def mark_unhealthy(self, worker_name: str) -> None:
        async with self._lock:
            for worker in self._workers:
                if worker.name == worker_name:
                    worker.healthy = False
                    worker.reconnecting = True
                    asyncio.create_task(self._reconnect_worker(worker))

    async def _reconnect_worker(self, worker: WorkerState) -> None:
        try:
            await worker.client.disconnect()
            await asyncio.sleep(5)
            await worker.client.connect()
            if await worker.client.is_user_authorized():
                async with self._lock:
                    worker.healthy = True
                    worker.reconnecting = False
                logger.info(f"Worker {worker.name} reconnected successfully.")
            else:
                logger.error(f"Worker {worker.name} failed to authorize after reconnect.")
        except Exception as e:
            logger.error(f"Error reconnecting worker {worker.name}: {e}")
            await asyncio.sleep(60)
            asyncio.create_task(self._reconnect_worker(worker))

    async def status(self) -> list[dict[str, str | bool]]:
        async with self._lock:
            return [
                {"name": w.name, "healthy": w.healthy, "reconnecting": w.reconnecting}
                for w in self._workers
            ]

    async def close(self):
        for w in self._workers:
            await w.client.disconnect()

worker_pool = WorkerPool()
