from __future__ import annotations

from play_cmd.history import HISTORY_LIMIT, add_history_item, last_history_item, read_history
from play_cmd.models import HistoryItem, ResultType


def test_add_history_item_dedupes_by_url_and_moves_to_top(tmp_path) -> None:
    path = tmp_path / "history.json"

    add_history_item(
        HistoryItem(title="Old", type=ResultType.direct, url="https://example.com/1"),
        path,
    )
    add_history_item(
        HistoryItem(title="Other", type=ResultType.video, url="https://example.com/2"),
        path,
    )
    add_history_item(
        HistoryItem(title="New", type=ResultType.playlist, url="https://example.com/1"),
        path,
    )

    items = read_history(path)

    assert [item.url for item in items] == ["https://example.com/1", "https://example.com/2"]
    assert items[0].title == "New"
    assert items[0].type is ResultType.playlist


def test_add_history_item_caps_at_limit(tmp_path) -> None:
    path = tmp_path / "history.json"

    for index in range(HISTORY_LIMIT + 5):
        add_history_item(
            HistoryItem(
                title=f"Item {index}",
                type=ResultType.video,
                url=f"https://example.com/{index}",
            ),
            path,
        )

    items = read_history(path)

    assert len(items) == HISTORY_LIMIT
    assert items[0].url == f"https://example.com/{HISTORY_LIMIT + 4}"
    assert items[-1].url == "https://example.com/5"


def test_last_history_item_returns_newest(tmp_path) -> None:
    path = tmp_path / "history.json"

    add_history_item(HistoryItem(title="First", url="https://example.com/1"), path)
    add_history_item(HistoryItem(title="Second", url="https://example.com/2"), path)

    item = last_history_item(path)

    assert item is not None
    assert item.title == "Second"
