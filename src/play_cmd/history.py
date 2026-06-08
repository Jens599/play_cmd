from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from play_cmd.models import HistoryItem, ResultType
from play_cmd.paths import history_path

HISTORY_LIMIT = 50


def read_history(path: Path | None = None) -> list[HistoryItem]:
    target = path or history_path()
    if not target.is_file():
        return []

    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
        return [HistoryItem.model_validate(item) for item in data]
    except (OSError, json.JSONDecodeError, ValidationError):
        return []


def write_history(items: list[HistoryItem], path: Path | None = None) -> Path:
    target = path or history_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps([item.model_dump(mode="json") for item in items], indent=2),
        encoding="utf-8",
    )
    return target


def add_history_item(item: HistoryItem, path: Path | None = None) -> list[HistoryItem]:
    existing = [entry for entry in read_history(path) if entry.url != item.url]
    items = [item, *existing][:HISTORY_LIMIT]
    write_history(items, path)
    return items


def record_playback(
    url: str,
    *,
    title: str | None = None,
    result_type: ResultType = ResultType.direct,
    path: Path | None = None,
) -> list[HistoryItem]:
    return add_history_item(
        HistoryItem(title=title or url, type=result_type, url=url),
        path,
    )


def last_history_item(path: Path | None = None) -> HistoryItem | None:
    items = read_history(path)
    return items[0] if items else None
