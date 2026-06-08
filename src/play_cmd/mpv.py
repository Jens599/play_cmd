from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from play_cmd.models import StreamFormat, WindowSize

FORMAT_MAP = {
    StreamFormat.p480: "bestvideo[height<=480]+bestaudio/best",
    StreamFormat.p720: "bestvideo[height<=720]+bestaudio/best",
    StreamFormat.p1080: "bestvideo[height<=1080]+bestaudio/best",
    StreamFormat.best: "bestvideo+bestaudio/best",
    StreamFormat.audio: "bestaudio/best",
}


@dataclass(frozen=True)
class Player:
    command: str
    display_name: str


@dataclass(frozen=True)
class PlaybackOptions:
    size: WindowSize = WindowSize.pip
    ytdl_format: StreamFormat = StreamFormat.p480
    cookie_path: str | None = None
    audio_only: bool = False
    loop: bool = False
    hardware_accel: bool = False
    background: bool = False
    reverse_playlist: bool = False
    no_subtitles: bool = False
    subtitle_language: list[str] = field(default_factory=lambda: ["en"])
    custom_args: list[str] = field(default_factory=list)


class PlayerNotFoundError(RuntimeError):
    pass


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_http_url(value: str) -> str:
    if not is_http_url(value):
        msg = "Invalid URL format. URLs should start with http:// or https://"
        raise ValueError(msg)
    return value


def player_candidates(player_path: str | None = None) -> list[str]:
    candidates: list[str] = []
    if player_path and player_path.strip():
        candidates.append(player_path.strip())

    candidates.extend(["mpv", "mpvnet.com", "mpvnet.exe"])

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        mpvnet_dir = Path(local_app_data) / "Programs" / "mpv.net"
        candidates.extend([str(mpvnet_dir / "mpvnet.com"), str(mpvnet_dir / "mpvnet.exe")])

    return candidates


def resolve_player(player_path: str | None = None) -> Player | None:
    for candidate in player_candidates(player_path):
        path = Path(candidate)
        if path.is_absolute() and path.is_file():
            resolved = str(path)
            return Player(command=resolved, display_name=resolved)

        resolved_command = shutil.which(candidate)
        if resolved_command:
            return Player(command=resolved_command, display_name=resolved_command)

    return None


def require_player(player_path: str | None = None) -> Player:
    player = resolve_player(player_path)
    if player is None:
        msg = "No media player found. Install mpv/mpv.net or configure a player path."
        raise PlayerNotFoundError(msg)
    return player


def build_mpv_args(options: PlaybackOptions) -> list[str]:
    args: list[str] = []
    if not options.background:
        args.append("--terminal=yes")

    match options.size:
        case WindowSize.pip:
            args.extend(["--geometry=320x180-10-10", "--autofit=320x180", "--no-border", "--ontop"])
        case WindowSize.small:
            args.extend(["--geometry=854x480-10-10", "--autofit=854x480"])
        case WindowSize.medium:
            args.extend(["--geometry=1280x720-10-10", "--autofit=1280x720"])
        case WindowSize.max:
            args.append("--fullscreen")

    if options.audio_only:
        args.append("--no-video")
    if options.loop:
        args.append("--loop=inf")
    if options.hardware_accel:
        args.append("--hwdec=auto")

    if options.reverse_playlist:
        args.extend(
            ["--ytdl-raw-options=playlist-items=1-", "--ytdl-raw-options=playlist-reverse="]
        )

    args.append(f"--ytdl-format={FORMAT_MAP[options.ytdl_format]}")

    if options.cookie_path:
        args.append(f"--ytdl-raw-options=cookies={options.cookie_path}")

    args.append("--ytdl-raw-options=no-download-archive=")

    if not options.no_subtitles:
        languages = options.subtitle_language or ["en"]
        args.append(f"--slang={','.join(languages)}")

    args.extend(options.custom_args)
    return args


def preview_command(command: list[str]) -> str:
    return shlex.join(command)


def launch_player(player: Player, args: list[str], background: bool = False) -> None:
    command = [player.command, *args]
    if background:
        popen_kwargs: dict[str, Any] = {
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "start_new_session": True,
        }
        if os.name == "nt":
            popen_kwargs["creationflags"] = (
                subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            )

        subprocess.Popen(command, **popen_kwargs)  # noqa: S603
        return

    subprocess.run(command, check=True)  # noqa: S603
