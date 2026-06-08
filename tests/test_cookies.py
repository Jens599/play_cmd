from __future__ import annotations

import pytest

from play_cmd.cookies import CookiePathError, find_default_cookie_path, resolve_cookie_path


def test_resolve_cookie_path_prefers_explicit_and_marks_saved(tmp_path) -> None:
    explicit = tmp_path / "explicit.txt"
    configured = tmp_path / "configured.txt"
    explicit.write_text("cookies", encoding="utf-8")
    configured.write_text("cookies", encoding="utf-8")

    resolved, should_save = resolve_cookie_path(
        str(explicit),
        str(configured),
        save_explicit=True,
    )

    assert resolved == str(explicit)
    assert should_save is True


def test_resolve_cookie_path_uses_configured_path(tmp_path) -> None:
    configured = tmp_path / "configured.txt"
    configured.write_text("cookies", encoding="utf-8")

    resolved, should_save = resolve_cookie_path(None, str(configured), save_explicit=True)

    assert resolved == str(configured)
    assert should_save is False


def test_resolve_cookie_path_validates_explicit_path(tmp_path) -> None:
    with pytest.raises(CookiePathError, match="does not exist"):
        resolve_cookie_path(str(tmp_path / "missing.txt"), None)


def test_find_default_cookie_path_returns_first_existing_candidate(tmp_path) -> None:
    missing = tmp_path / "missing.txt"
    existing = tmp_path / "cookies.txt"
    existing.write_text("cookies", encoding="utf-8")

    assert find_default_cookie_path([missing, existing]) == str(existing)
