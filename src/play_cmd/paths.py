from __future__ import annotations

from pathlib import Path

from platformdirs import user_config_path

APP_NAME = "play-cmd"


def app_config_dir() -> Path:
    return user_config_path(APP_NAME)


def config_path() -> Path:
    return app_config_dir() / "config.json"


def history_path() -> Path:
    return app_config_dir() / "history.json"
