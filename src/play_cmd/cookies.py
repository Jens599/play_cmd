from __future__ import annotations

import os
from pathlib import Path


class CookiePathError(ValueError):
    pass


def default_cookie_candidates() -> list[Path]:
    candidates: list[Path] = []
    home = Path.home()
    candidates.extend(
        [
            home / "cookies.txt",
            home / "Downloads" / "cookies.txt",
            Path.cwd() / "cookies.txt",
        ]
    )

    app_data = os.environ.get("APPDATA")
    if app_data:
        candidates.append(Path(app_data) / "play-cmd" / "cookies.txt")

    return candidates


def validate_cookie_path(path: str | Path) -> str:
    candidate = Path(path).expanduser()
    if not candidate.is_file():
        msg = f"Cookie file does not exist: {candidate}"
        raise CookiePathError(msg)
    return str(candidate)


def find_default_cookie_path(candidates: list[Path] | None = None) -> str | None:
    for candidate in candidates or default_cookie_candidates():
        expanded = candidate.expanduser()
        if expanded.is_file():
            return str(expanded)
    return None


def resolve_cookie_path(
    explicit_path: str | None,
    configured_path: str | None,
    *,
    save_explicit: bool = False,
) -> tuple[str | None, bool]:
    if explicit_path:
        resolved = validate_cookie_path(explicit_path)
        return resolved, save_explicit

    if configured_path:
        return validate_cookie_path(configured_path), False

    return find_default_cookie_path(), False
