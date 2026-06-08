from __future__ import annotations

import subprocess

import pytest

from play_cmd.models import ResultType
from play_cmd.search import (
    SEARCH_PRINT_TEMPLATE,
    SearchError,
    build_search_url,
    build_ytdlp_search_args,
    detect_result_type,
    parse_search_row,
    search_youtube,
)


def test_build_search_url_encodes_query() -> None:
    assert build_search_url("lofi beats") == (
        "https://www.youtube.com/results?search_query=lofi%20beats"
    )


def test_build_search_url_adds_playlist_parameter() -> None:
    assert build_search_url("lofi", playlist=True).endswith("&sp=EgIQAw%3D%3D")


def test_build_ytdlp_search_args_includes_flat_playlist_limit_and_cookies() -> None:
    args = build_ytdlp_search_args(
        "lofi beats",
        max_results=12,
        playlist=True,
        cookie_path="cookies.txt",
    )

    assert args[0] == "https://www.youtube.com/results?search_query=lofi%20beats&sp=EgIQAw%3D%3D"
    assert args[1:6] == [
        "--print",
        SEARCH_PRINT_TEMPLATE,
        "--flat-playlist",
        "--playlist-items",
        "1:12",
    ]
    assert args[-2:] == ["--cookies", "cookies.txt"]


def test_build_ytdlp_search_args_validates_max_results() -> None:
    with pytest.raises(ValueError, match="max_results"):
        build_ytdlp_search_args("lofi", max_results=0)


def test_detect_result_type_playlist() -> None:
    assert (
        detect_result_type("PL123", "YoutubePlaylist", "https://youtube.com/playlist?list=PL123")
        is ResultType.playlist
    )


def test_detect_result_type_channel() -> None:
    assert (
        detect_result_type("UC123", "YoutubeTab", "https://youtube.com/@example")
        is ResultType.channel
    )


def test_detect_result_type_video() -> None:
    assert (
        detect_result_type("abc123", "Youtube", "https://youtube.com/watch?v=abc123")
        is ResultType.video
    )


def test_parse_search_row_builds_result() -> None:
    result = parse_search_row(
        "Video Title\tabc123\tYoutube\thttps://youtube.com/watch?v=abc123\t3:21\tUploader\t12345"
    )

    assert result is not None
    assert result.title == "Video Title"
    assert result.id == "abc123"
    assert result.type is ResultType.video
    assert result.url == "https://youtube.com/watch?v=abc123"
    assert result.duration == "3:21"
    assert result.uploader == "Uploader"
    assert result.view_count == "12345"
    assert result.menu_title == "[Video] Video Title | 3:21 | Uploader | 12,345 views"


def test_parse_search_row_ignores_invalid_row() -> None:
    assert parse_search_row("missing-fields") is None


def test_search_youtube_filters_result_type(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=(
                "Video\tvid123\tYoutube\thttps://youtube.com/watch?v=vid123\t1:00\tUploader\t10\n"
                "Playlist\tPL123\tYoutubePlaylist\thttps://youtube.com/playlist?list=PL123\tNA\tUploader\tNA\n"
            ),
            stderr="",
        )

    monkeypatch.setattr("play_cmd.search.shutil.which", lambda command: "yt-dlp")
    monkeypatch.setattr("play_cmd.search.subprocess.run", fake_run)

    results = search_youtube("lofi", max_results=10, result_type=ResultType.playlist)

    assert len(results) == 1
    assert results[0].type is ResultType.playlist
    assert results[0].title == "Playlist"


def test_search_youtube_raises_search_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=args, returncode=1, stdout="", stderr="boom")

    monkeypatch.setattr("play_cmd.search.shutil.which", lambda command: "yt-dlp")
    monkeypatch.setattr("play_cmd.search.subprocess.run", fake_run)

    with pytest.raises(SearchError, match="boom"):
        search_youtube("lofi", max_results=10)
