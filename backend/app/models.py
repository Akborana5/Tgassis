from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class MediaType(str, Enum):
    movie = "movie"
    anime = "anime"
    series = "series"


class MediaFile(BaseModel):
    telegram_channel: str
    message_id: int
    quality: str
    language: str
    codec: str | None = None
    source: str | None = None
    size: int | None = None
    assistant_bot: str | None = None
    mime_type: str | None = None
    filename: str
    local_path: str | None = None


class MediaItem(BaseModel):
    id: str
    title: str
    year: int | None = None
    description: str = ""
    genre: list[str] = Field(default_factory=list)
    qualities: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    versions: list[str] = Field(default_factory=list)
    media_type: MediaType = MediaType.movie
    poster: str | None = None
    runtime: int | None = None
    seasons: list[int] = Field(default_factory=list)
    episodes: list[int] = Field(default_factory=list)
    files: list[MediaFile] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SearchResult(BaseModel):
    id: str
    title: str
    year: int | None
    poster: str | None
    languages: list[str]
    qualities: list[str]
    score: float


class SearchResponse(BaseModel):
    query: str
    page: int
    page_size: int
    total: int
    items: list[SearchResult]


class AdminActionResponse(BaseModel):
    status: Literal["queued", "done"]
    detail: str
