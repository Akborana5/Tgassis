from __future__ import annotations

import re
from dataclasses import dataclass

QUALITY_PATTERNS = ["2160p", "1080p", "720p", "480p", "360p", "4k", "hdr"]
LANGUAGE_PATTERNS = [
    "hindi",
    "english",
    "tamil",
    "telugu",
    "malayalam",
    "dual audio",
    "multi audio",
]
CODEC_PATTERNS = ["hevc", "x264", "x265", "av1"]
SOURCE_PATTERNS = ["web-dl", "bluray", "hdrip", "dvdrip", "predvd", "cam"]


@dataclass(slots=True)
class ParsedMetadata:
    title: str
    quality: str | None
    language: str | None
    codec: str | None
    source: str | None
    year: int | None


def _find_any(patterns: list[str], haystack: str) -> str | None:
    lowered = haystack.lower()
    for pattern in patterns:
        if pattern in lowered:
            return pattern.upper() if pattern in {"x264", "x265", "av1", "hevc"} else pattern.title()
    return None


def parse_metadata_from_filename(filename: str) -> ParsedMetadata:
    quality = _find_any(QUALITY_PATTERNS, filename)
    language = _find_any(LANGUAGE_PATTERNS, filename)
    codec = _find_any(CODEC_PATTERNS, filename)
    source = _find_any(SOURCE_PATTERNS, filename)

    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", filename)
    year = int(year_match.group(1)) if year_match else None

    cleaned = re.sub(r"[._-]+", " ", filename)
    cleaned = re.sub(r"\b(19\d{2}|20\d{2})\b", "", cleaned)
    for token in QUALITY_PATTERNS + LANGUAGE_PATTERNS + CODEC_PATTERNS + SOURCE_PATTERNS:
        cleaned = re.sub(re.escape(token), "", cleaned, flags=re.IGNORECASE)
    title = re.sub(r"\s+", " ", cleaned).strip(" .-") or filename

    return ParsedMetadata(
        title=title.title(),
        quality=quality,
        language=language,
        codec=codec,
        source=source,
        year=year,
    )
