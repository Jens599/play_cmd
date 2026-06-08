from __future__ import annotations

import os
from pathlib import Path

import pytest

from play_cmd.models import StreamFormat, WindowSize
from play_cmd.mpv import (
    PlaybackOptions,
    Player,
    build_mpv_args,
    launch_player,
    player_candidates,
    preview_command,
    resolve_player,
    validate_http_url,
)


def test_build_default_mpv_args() -> None:
    args = build_mpv_args(PlaybackOptions())

    assert "--terminal=yes" in args
    assert "--geometry=320x180-10-10" in args
    assert "--autofit=320x180" in args
    assert "--no-border" in args
    assert "--ontop" in args
    assert "--ytdl-format=bestvideo[height<=480]+bestaudio/best" in args
    assert "--ytdl-raw-options=no-download-archive=" in args
    assert "--slang=en" in args


def test_build_medium_720p_audio_loop_hw_args() -> None:
    args = build_mpv_args(
        PlaybackOptions(
            size=WindowSize.medium,
            ytdl_format=StreamFormat.p720,
            audio_only=True,
            loop=True,
            hardware_accel=True,
            subtitle_language=["en", "ja"],
            custom_args=["--speed=1.25"],
        )
    )

    assert "--geometry=1280x720-10-10" in args
    assert "--autofit=1280x720" in args
    assert "--ytdl-format=bestvideo[height<=720]+bestaudio/best" in args
    assert "--no-video" in args
    assert "--loop=inf" in args
    assert "--hwdec=auto" in args
    assert "--slang=en,ja" in args
    assert args[-1] == "--speed=1.25"


def test_background_omits_terminal_and_no_subtitles_omits_slang() -> None:
    args = build_mpv_args(PlaybackOptions(background=True, no_subtitles=True))

    assert "--terminal=yes" not in args
    assert not any(arg.startswith("--slang=") for arg in args)


def test_reverse_playlist_and_cookie_args() -> None:
    args = build_mpv_args(
        PlaybackOptions(cookie_path="C:/Users/Dell/cookies.txt", reverse_playlist=True)
    )

    assert "--ytdl-raw-options=playlist-items=1-" in args
    assert "--ytdl-raw-options=playlist-reverse=" in args
    assert "--ytdl-raw-options=cookies=C:/Users/Dell/cookies.txt" in args


def test_max_size_uses_fullscreen() -> None:
    args = build_mpv_args(PlaybackOptions(size=WindowSize.max))

    assert "--fullscreen" in args


def test_player_candidates_include_configured_and_local_mpvnet(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", "C:/Users/Dell/AppData/Local")

    candidates = player_candidates("custom-mpv")

    assert candidates[0] == "custom-mpv"
    assert candidates[1:4] == ["mpv", "mpvnet.com", "mpvnet.exe"]
    assert candidates[-2:] == [
        os.fspath(Path("C:/Users/Dell/AppData/Local") / "Programs" / "mpv.net" / "mpvnet.com"),
        os.fspath(Path("C:/Users/Dell/AppData/Local") / "Programs" / "mpv.net" / "mpvnet.exe"),
    ]


def test_resolve_player_prefers_absolute_file(tmp_path) -> None:
    player_file = tmp_path / "mpv.exe"
    player_file.write_text("", encoding="utf-8")

    player = resolve_player(str(player_file))

    assert player == Player(command=str(player_file), display_name=str(player_file))


def test_validate_http_url_accepts_http_and_https() -> None:
    assert validate_http_url("https://example.com/video") == "https://example.com/video"
    assert validate_http_url("http://example.com/video") == "http://example.com/video"


def test_validate_http_url_rejects_invalid_url() -> None:
    with pytest.raises(ValueError, match="Invalid URL format"):
        validate_http_url("not a url")


def test_preview_command_quotes_arguments_with_spaces() -> None:
    preview = preview_command(["mpv", "--title=hello world", "https://example.com/watch?v=1"])

    assert "mpv" in preview
    assert "hello world" in preview
    assert "https://example.com/watch?v=1" in preview


def test_launch_player_uses_run_for_foreground(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[list[str], bool]] = []

    def fake_run(command: list[str], check: bool) -> None:
        calls.append((command, check))

    monkeypatch.setattr("play_cmd.mpv.subprocess.run", fake_run)

    launch_player(Player(command="mpv", display_name="mpv"), ["--fullscreen", "https://example.com"])

    assert calls == [(["mpv", "--fullscreen", "https://example.com"], True)]


def test_launch_player_uses_popen_for_background(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[list[str], bool]] = []

    class FakeProcess:
        pass

    def fake_popen(command: list[str], start_new_session: bool) -> FakeProcess:
        calls.append((command, start_new_session))
        return FakeProcess()

    monkeypatch.setattr("play_cmd.mpv.subprocess.Popen", fake_popen)

    launch_player(
        Player(command="mpv", display_name="mpv"),
        ["--no-video", "https://example.com"],
        background=True,
    )

    assert calls == [(["mpv", "--no-video", "https://example.com"], True)]
