from __future__ import annotations

from pathlib import Path
from threading import Lock

import orjson

from .config import settings
from .huggingface import hf_sync
from .models import MediaItem, MediaType


class MediaStore:
    def __init__(self, path: Path):
        self.path = path
        self.lock = Lock()
        self._media: dict[str, MediaItem] = {}
        hf_sync.sync_database_down()
        self._ensure_seed()
        self._load()

    def _ensure_seed(self) -> None:
        if self.path.exists():
            return
        sample = {
            "items": [
                {
                    "id": "avengers-endgame-2019",
                    "title": "Avengers Endgame",
                    "year": 2019,
                    "description": "After the Snap, the Avengers assemble for one final mission.",
                    "genre": ["Action", "Sci-Fi"],
                    "qualities": ["480p", "720p", "1080p"],
                    "languages": ["English", "Hindi"],
                    "versions": ["Original", "Dual Audio"],
                    "media_type": "movie",
                    "runtime": 181,
                    "files": [
                        {
                            "telegram_channel": "MoviesDB",
                            "message_id": 1001,
                            "quality": "1080p",
                            "language": "English",
                            "codec": "x265",
                            "source": "WEB-DL",
                            "size": 2147483648,
                            "assistant_bot": "worker1",
                            "filename": "avengers_endgame_1080p.mkv",
                            "mime_type": "video/x-matroska",
                            "local_path": None,
                        }
                    ],
                },
                {
                    "id": "one-piece",
                    "title": "One Piece",
                    "year": 1999,
                    "description": "Straw Hat pirates chase the greatest treasure.",
                    "genre": ["Anime", "Adventure"],
                    "qualities": ["720p", "1080p"],
                    "languages": ["Japanese", "English"],
                    "versions": ["Subbed", "Dubbed"],
                    "media_type": "anime",
                    "seasons": [1],
                    "episodes": [1, 2, 3],
                    "files": [],
                },
            ]
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(orjson.dumps(sample, option=orjson.OPT_INDENT_2))

    def _load(self) -> None:
        payload = orjson.loads(self.path.read_bytes())
        self._media = {
            row["id"]: MediaItem.model_validate(row) for row in payload.get("items", [])
        }

    def _save(self) -> None:
        data = {"items": [item.model_dump(mode="json") for item in self._media.values()]}
        self.path.write_bytes(orjson.dumps(data, option=orjson.OPT_INDENT_2))
        import asyncio
        asyncio.get_event_loop().run_in_executor(None, hf_sync.sync_database_up)

    def all(self) -> list[MediaItem]:
        return sorted(self._media.values(), key=lambda i: i.created_at, reverse=True)

    def get(self, media_id: str) -> MediaItem | None:
        return self._media.get(media_id)

    def by_type(self, media_type: MediaType) -> list[MediaItem]:
        return [item for item in self.all() if item.media_type == media_type]

    def upsert(self, item: MediaItem) -> None:
        with self.lock:
            self._media[item.id] = item
            self._save()


store = MediaStore(settings.database_path)
