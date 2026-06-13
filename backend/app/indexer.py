from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
import os

from telethon import TelegramClient
from .dedupe import merge_duplicates
from .metadata import parse_metadata_from_filename
from .models import MediaFile, MediaItem, MediaType
from .storage import store
from .workers import worker_pool

logger = logging.getLogger(__name__)

@dataclass(slots=True)
class IndexerConfig:
    scan_interval_seconds: int = int(os.getenv("SCAN_INTERVAL", "300"))
    channels: list[str] = ("@Anime_Gallery",) # Replace with real channels or env var

class TelegramIndexer:
    def __init__(self, config: IndexerConfig | None = None):
        self.config = config or IndexerConfig()
        channels_env = os.getenv("INDEX_CHANNELS")
        if channels_env:
            self.config.channels = [c.strip() for c in channels_env.split(",")]

    async def scan_once(self) -> int:
        worker = await worker_pool.next_worker()
        if not worker:
            logger.warning("No workers available for scanning.")
            return 0

        client = worker.client
        new_items = []
        for channel in self.config.channels:
            try:
                entity = await client.get_entity(channel)
                # Fetch recent messages that have media
                async for message in client.iter_messages(entity, limit=100, filter=None):
                    if not message.media or not hasattr(message.media, "document"):
                        continue
                        
                    doc = message.media.document
                    if not doc:
                        continue

                    # Find filename
                    filename = "unknown.mkv"
                    for attr in doc.attributes:
                        if hasattr(attr, "file_name"):
                            filename = attr.file_name
                            break
                    
                    parsed = parse_metadata_from_filename(filename)
                    media_id = f"{parsed.title.lower().replace(' ', '-')}-{parsed.year or 'unknown'}"
                    
                    # See if already indexed
                    existing = store.get(media_id)
                    already_has_file = False
                    if existing:
                        for f in existing.files:
                            if f.message_id == message.id and f.telegram_channel == channel:
                                already_has_file = True
                                break
                    if already_has_file:
                        continue

                    item = MediaItem(
                        id=media_id,
                        title=parsed.title,
                        year=parsed.year,
                        qualities=[parsed.quality] if parsed.quality else [],
                        languages=[parsed.language] if parsed.language else [],
                        versions=["Original"],
                        media_type=MediaType.movie, # Might need better parsing
                        files=[
                            MediaFile(
                                telegram_channel=channel,
                                message_id=message.id,
                                quality=parsed.quality or "unknown",
                                language=parsed.language or "unknown",
                                codec=parsed.codec,
                                source=parsed.source,
                                size=doc.size,
                                filename=filename,
                                mime_type=doc.mime_type
                            )
                        ],
                    )
                    new_items.append(item)
            except Exception as e:
                logger.error(f"Error scanning channel {channel}: {e}")

        # Combine new items with existing and dedupe
        if new_items:
            all_items = store.all() + new_items
            merged = merge_duplicates(all_items)
            for item in merged:
                store.upsert(item)
                
        return len(new_items)

    async def run_forever(self) -> None:
        while True:
            try:
                count = await self.scan_once()
                logger.info(f"Scanned {count} new items")
            except Exception as e:
                logger.error(f"Error in background indexer: {e}")
            await asyncio.sleep(self.config.scan_interval_seconds)

indexer = TelegramIndexer()
