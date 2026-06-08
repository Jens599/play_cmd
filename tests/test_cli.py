from __future__ import annotations

from play_cmd.cli import normalize_root_args


def test_normalize_root_args_moves_target_after_trailing_options() -> None:
    assert normalize_root_args(["-s", "beghast", "-t", "Video", "--first", "-b"]) == [
        "-s",
        "-t",
        "Video",
        "--first",
        "-b",
        "beghast",
    ]


def test_normalize_root_args_preserves_command_args() -> None:
    assert normalize_root_args(["search", "beghast", "-t", "Video"]) == [
        "search",
        "beghast",
        "-t",
        "Video",
    ]


def test_normalize_root_args_preserves_options_before_target() -> None:
    assert normalize_root_args(["-s", "-t", "Video", "beghast"]) == [
        "-s",
        "-t",
        "Video",
        "beghast",
    ]
