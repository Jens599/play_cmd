from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from play_cmd.models import AppConfig
from play_cmd.paths import config_path


def default_config() -> AppConfig:
    return AppConfig()


def read_config(path: Path | None = None) -> AppConfig:
    target = path or config_path()
    if not target.is_file():
        return default_config()

    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        return AppConfig.model_validate(data)
    except (OSError, json.JSONDecodeError, ValidationError):
        return default_config()


def save_config(config: AppConfig, path: Path | None = None) -> Path:
    target = path or config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(config.model_dump_json(indent=2), encoding="utf-8")
    return target


def reset_config(path: Path | None = None) -> AppConfig:
    config = default_config()
    save_config(config, path)
    return config
