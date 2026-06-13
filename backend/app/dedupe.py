from __future__ import annotations

from collections import defaultdict

from .models import MediaFile, MediaItem, MediaType


def normalize_key(title: str, year: int | None, media_type: MediaType) -> str:
    normalized = " ".join(title.lower().split())
    return f"{media_type.value}:{normalized}:{year or 'unknown'}"


def merge_duplicates(items: list[MediaItem]) -> list[MediaItem]:
    grouped: dict[str, list[MediaItem]] = defaultdict(list)
    for item in items:
        grouped[normalize_key(item.title, item.year, item.media_type)].append(item)

    merged: list[MediaItem] = []
    for chunk in grouped.values():
        head = chunk[0]
        qualities = sorted({quality for entry in chunk for quality in entry.qualities})
        languages = sorted({language for entry in chunk for language in entry.languages})
        versions = sorted({version for entry in chunk for version in entry.versions})
        files: list[MediaFile] = [f for entry in chunk for f in entry.files]

        merged.append(
            head.model_copy(
                update={
                    "qualities": qualities,
                    "languages": languages,
                    "versions": versions,
                    "files": files,
                }
            )
        )
    return merged
