from __future__ import annotations

import pyperclip  # type: ignore[import-untyped]


class ClipboardError(RuntimeError):
    pass


def read_clipboard_text() -> str:
    try:
        text = pyperclip.paste()
    except pyperclip.PyperclipException as error:
        msg = f"Clipboard is unavailable: {error}"
        raise ClipboardError(msg) from error

    if not isinstance(text, str) or not text.strip():
        msg = "Clipboard does not contain text."
        raise ClipboardError(msg)
    return text.strip()
