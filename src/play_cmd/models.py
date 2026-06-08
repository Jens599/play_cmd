from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class WindowSize(StrEnum):
    pip = "PIP"
    small = "Small"
    medium = "Medium"
    max = "Max"


class StreamFormat(StrEnum):
    p480 = "480p"
    p720 = "720p"
    p1080 = "1080p"
    best = "best"
    audio = "audio"


class ResultType(StrEnum):
    video = "Video"
    playlist = "Playlist"
    channel = "Channel"
    direct = "Direct"
    search = "Search"


class AppConfig(BaseModel):
    cookie_path: str | None = None
    player_path: str | None = None
    default_size: WindowSize = WindowSize.pip
    default_format: StreamFormat = StreamFormat.p480
    max_results: int = Field(default=10, ge=1, le=50)
    audio_only: bool = False
    background: bool = False
    loop: bool = False
    hardware_accel: bool = False
    reverse_playlist: bool = False
    no_subtitles: bool = False
    subtitle_language: list[str] = Field(default_factory=lambda: ["en"])
    theme: str = "neon-dark"

    @field_validator("subtitle_language", mode="before")
    @classmethod
    def normalize_subtitle_language(cls, value: object) -> list[str]:
        if value is None:
            return ["en"]
        if isinstance(value, str):
            parts = [part.strip() for part in value.split(",")]
            return [part for part in parts if part] or ["en"]
        if isinstance(value, list):
            parts = [str(part).strip() for part in value]
            return [part for part in parts if part] or ["en"]
        return ["en"]


class SearchResult(BaseModel):
    title: str
    id: str
    type: ResultType
    url: str
    duration: str | None = None
    uploader: str | None = None
    view_count: int | str | None = None
    menu_title: str | None = None


class HistoryItem(BaseModel):
    title: str
    type: ResultType = ResultType.direct
    url: str
    played_at: datetime = Field(default_factory=datetime.now)
    menu_title: str | None = None
