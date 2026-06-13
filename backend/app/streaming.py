from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator, Iterator

from fastapi import HTTPException
from starlette import status
from telethon import TelegramClient

logger = logging.getLogger(__name__)

@dataclass(slots=True)
class ByteRange:
    start: int
    end: int


def parse_range(range_header: str | None, file_size: int) -> ByteRange:
    if not range_header:
        return ByteRange(0, file_size - 1)
    if not range_header.startswith("bytes="):
        raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE, detail="Invalid range unit")

    value = range_header.removeprefix("bytes=")
    start_text, _, end_text = value.partition("-")
    if start_text == "":
        suffix = int(end_text)
        if suffix <= 0:
            raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE, detail="Invalid suffix")
        start = max(0, file_size - suffix)
        end = file_size - 1
    else:
        start = int(start_text)
        end = int(end_text) if end_text else file_size - 1

    if start < 0 or end >= file_size or start > end:
        raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE, detail="Invalid byte range")
    return ByteRange(start, end)


def file_chunk_iterator(path: Path, byte_range: ByteRange, chunk_size: int = 1024 * 1024) -> Iterator[bytes]:
    with path.open("rb") as handle:
        handle.seek(byte_range.start)
        remaining = byte_range.end - byte_range.start + 1
        while remaining > 0:
            chunk = handle.read(min(chunk_size, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk


async def telegram_chunk_iterator(
    client: TelegramClient,
    channel: str,
    message_id: int,
    byte_range: ByteRange,
    chunk_size: int = 1024 * 1024
) -> AsyncIterator[bytes]:
    try:
        # Resolve the channel entity and message
        entity = await client.get_entity(channel)
        message = await client.get_messages(entity, ids=message_id)
        if not message or not message.media:
            logger.error(f"Message {message_id} in {channel} has no media.")
            yield b""
            return

        remaining = byte_range.end - byte_range.start + 1
        
        # We need to offset iter_download correctly
        # iter_download takes offset and chunk_size. But offset must be a multiple of chunk_size typically for Telegram API
        # To simplify, we just download required bytes.
        
        async for chunk in client.iter_download(message.media, offset=byte_range.start):
            if remaining <= 0:
                break
            if len(chunk) > remaining:
                chunk = chunk[:remaining]
            remaining -= len(chunk)
            yield chunk
            
    except Exception as e:
        logger.error(f"Telegram stream error: {e}")
        raise
