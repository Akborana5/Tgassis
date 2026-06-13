from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from fastapi import HTTPException
from starlette import status


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
