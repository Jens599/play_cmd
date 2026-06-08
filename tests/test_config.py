from __future__ import annotations

from play_cmd.config import default_config, read_config, reset_config, save_config
from play_cmd.models import StreamFormat, WindowSize


def test_default_config_values() -> None:
    config = default_config()

    assert config.cookie_path is None
    assert config.player_path is None
    assert config.default_size is WindowSize.pip
    assert config.default_format is StreamFormat.p480
    assert config.max_results == 10
    assert config.subtitle_language == ["en"]


def test_config_save_and_load(tmp_path) -> None:
    path = tmp_path / "config.json"
    config = default_config()
    config.default_size = WindowSize.medium
    config.subtitle_language = ["en", "ja"]

    save_config(config, path)
    loaded = read_config(path)

    assert loaded.default_size is WindowSize.medium
    assert loaded.subtitle_language == ["en", "ja"]


def test_read_config_returns_default_for_missing_file(tmp_path) -> None:
    loaded = read_config(tmp_path / "missing.json")

    assert loaded == default_config()


def test_reset_config_writes_defaults(tmp_path) -> None:
    path = tmp_path / "config.json"

    reset = reset_config(path)
    loaded = read_config(path)

    assert reset == default_config()
    assert loaded == default_config()
