from __future__ import annotations

from play_cmd.paths import APP_NAME, config_path, history_path


def test_paths_use_app_name() -> None:
    assert APP_NAME in str(config_path())
    assert APP_NAME in str(history_path())
    assert config_path().name == "config.json"
    assert history_path().name == "history.json"
