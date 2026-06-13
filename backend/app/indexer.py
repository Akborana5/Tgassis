from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path

from .dedupe import merge_duplicates
from .metadata import parse_metadata_from_filename
from .models import MediaFile, MediaItem, MediaType
from .storage import store


@dataclass(slots=True)
class IndexerConfig:
    scan_interval_seconds: int = 300
    sessions_dir: Path = Path(__file__).resolve().parents[1] / "data" / "sessions"


class TelegramIndexer:
    """Async indexer scaffold. Telegram pulling is intentionally abstracted behind worker bots."""

    def __init__(self, config: IndexerConfig | None = None):
        self.config = config or IndexerConfig()
        self.config.sessions_dir.mkdir(parents=True, exist_ok=True)

    def available_sessions(self) -> list[str]:
        return sorted(path.name for path in self.config.sessions_dir.glob("*.session"))

    async def scan_once(self) -> int:
        # Placeholder for Telethon workers; keeps architecture ready without exposing links.
        all_items = merge_duplicates(store.all())
        for item in all_items:
            store.upsert(item)
        await asyncio.sleep(0)
        return len(all_items)

    async def run_forever(self) -> None:
        while True:
            await self.scan_once()
            await asyncio.sleep(self.config.scan_interval_seconds)


async def index_single_filename(filename: str, channel: str, message_id: int) -> MediaItem:
    parsed = parse_metadata_from_filename(filename)
    media_id = f"{parsed.title.lower().replace(' ', '-')}-{parsed.year or 'unknown'}"
    item = MediaItem(
        id=media_id,
        title=parsed.title,
        year=parsed.year,
        qualities=[parsed.quality] if parsed.quality else [],
        languages=[parsed.language] if parsed.language else [],
        versions=["Original"],
        media_type=MediaType.movie,
        files=[
            MediaFile(
                telegram_channel=channel,
                message_id=message_id,
                quality=parsed.quality or "unknown",
                language=parsed.language or "unknown",
                codec=parsed.codec,
                source=parsed.source,
                filename=filename,
            )
        ],
    )
    store.upsert(item)
    return item
