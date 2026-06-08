from __future__ import annotations

import pyperclip
import pytest

from play_cmd.clipboard import ClipboardError, read_clipboard_text


def test_read_clipboard_text_strips_text(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("play_cmd.clipboard.pyperclip.paste", lambda: "  https://example.com  ")

    assert read_clipboard_text() == "https://example.com"


def test_read_clipboard_text_rejects_empty_text(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("play_cmd.clipboard.pyperclip.paste", lambda: "  ")

    with pytest.raises(ClipboardError, match="does not contain text"):
        read_clipboard_text()


def test_read_clipboard_text_wraps_pyperclip_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_error() -> str:
        raise pyperclip.PyperclipException("missing backend")

    monkeypatch.setattr("play_cmd.clipboard.pyperclip.paste", raise_error)

    with pytest.raises(ClipboardError, match="Clipboard is unavailable"):
        read_clipboard_text()
