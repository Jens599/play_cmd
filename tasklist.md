# Start-MPVStream Python Port Tasklist

## Phase 1: uv Scaffold and Core CLI

- [x] Initialize app with `uv init --app --package play-cmd`.
- [x] Pin Python version with `uv python pin 3.13`.
- [x] Add runtime dependencies: `typer`, `rich`, `textual`, `pydantic`, `platformdirs`, `pyperclip`.
- [x] Add dev dependencies: `ruff`, `pytest`, `pytest-cov`, `mypy`, `pyinstaller`.
- [x] Create package structure under `src/play_cmd/`.
- [x] Add console script: `play`.
- [x] Implement Typer CLI entrypoint.
- [x] Add placeholder commands: `config`, `history`, `search`, `tui`, `doctor`.
- [x] Add Pydantic models for config, search results, and history items.
- [x] Add app-data path helpers with `platformdirs`.
- [x] Implement config defaults, load, save, and reset.
- [x] Add tests for config defaults and config save/load.
- [x] Verify `uv run play --help`.
- [x] Verify `uv run pytest`.
- [x] Verify `uv run ruff check .`.

## Phase 2: mpv Playback Parity

- [x] Implement player resolution from configured path.
- [x] Implement fallback player lookup for `mpv`, `mpvnet.com`, and `mpvnet.exe`.
- [x] Implement local mpv.net lookup under `%LOCALAPPDATA%\Programs\mpv.net`.
- [x] Implement URL validation for HTTP/HTTPS URLs.
- [x] Implement quality/format mapping.
- [x] Implement size/window argument mapping.
- [x] Implement audio-only argument handling.
- [x] Implement loop argument handling.
- [x] Implement hardware acceleration argument handling.
- [x] Implement background playback process launch.
- [x] Implement reverse playlist arguments.
- [x] Implement subtitle language and no-subtitle handling.
- [x] Implement custom mpv argument passthrough.
- [x] Implement dry-run command preview.
- [x] Add tests for mpv argument generation.
- [x] Add tests for player resolution ordering.
- [x] Verify direct URL dry-run playback command.

## Phase 3: Search Parity

- [x] Implement `yt-dlp` dependency check.
- [x] Implement YouTube search URL construction.
- [x] Implement playlist-only search parameter.
- [x] Implement `yt-dlp` flat-playlist command construction.
- [x] Implement cookie forwarding to `yt-dlp`.
- [x] Parse `yt-dlp` tab-separated search rows.
- [x] Detect result type: Video, Playlist, Channel.
- [x] Implement result type filtering.
- [x] Implement max result limiting.
- [x] Implement `--first` behavior.
- [x] Implement initial Rich table/basic picker fallback.
- [x] Add tests for row parsing.
- [x] Add tests for result type detection.
- [x] Add tests for filtering.
- [x] Verify `uv run play "lofi beats" --search --first --dry-run`.

## Phase 4: History, Clipboard, Cookies

- [x] Implement clipboard text retrieval.
- [x] Implement history file path.
- [x] Implement history read/write.
- [x] Implement history de-dupe by URL.
- [x] Cap history at 50 entries.
- [x] Implement replay last history item.
- [x] Implement interactive history selection.
- [x] Implement cookie path precedence from config.
- [x] Implement explicit cookie path validation.
- [x] Save explicit cookie path to config.
- [x] Implement default cookie path lookup.
- [x] Add tests for history de-dupe and cap behavior.
- [x] Add tests for cookie path precedence.
- [x] Verify `uv run play --clipboard --dry-run`.
- [x] Verify `uv run play --last --dry-run`.
- [x] Verify `uv run play history`.

## Phase 5: Modern Textual TUI

- [ ] Create shared Textual theme.
- [ ] Create shared keyboard shortcut/footer system.
- [ ] Build search screen layout.
- [ ] Add search query input and filter chips.
- [ ] Add result list with media metadata.
- [ ] Add selected-result detail pane.
- [ ] Add loading state.
- [ ] Add empty state.
- [ ] Add error state.
- [ ] Add play, audio, format, size, copy URL, and dry-run actions.
- [ ] Build history screen.
- [ ] Add fuzzy filtering for history.
- [ ] Add grouped history sections.
- [ ] Add replay, delete item, and clear history actions.
- [ ] Build settings screen.
- [ ] Add player path editor with validation.
- [ ] Add cookie path editor with validation.
- [ ] Add size, format, subtitle, and toggle controls.
- [ ] Add dependency status cards.
- [ ] Integrate TUI picker into CLI search flow.
- [ ] Integrate TUI picker into CLI history flow.
- [ ] Verify `uv run play tui`.
- [ ] Verify interactive search playback flow.

## Phase 6: Doctor, Polish, Packaging

- [ ] Implement `play doctor` dependency checks.
- [ ] Show detected paths and versions for `mpv`, `mpv.net`, and `yt-dlp`.
- [ ] Show cookie/config/history status.
- [ ] Add install/fix hints for missing dependencies.
- [ ] Add copyable diagnostics summary.
- [ ] Add README usage examples.
- [ ] Add shell completion instructions.
- [ ] Add formatting/lint/typecheck scripts or documented commands.
- [ ] Add optional PyInstaller build configuration.
- [ ] Verify `uv run play doctor`.
- [ ] Verify `uv run ruff format --check .`.
- [ ] Verify `uv run ruff check .`.
- [ ] Verify `uv run mypy src`.
- [ ] Verify `uv run pytest --cov=play_cmd`.

## Decisions To Track

- [x] Use `play` as the primary installed command.
- [x] Start fresh; do not import legacy PowerShell config/history in v1.
- [x] Use install instructions only; do not auto-install dependencies.
- [x] Do not build a web UI or desktop web shell.
- [x] Design cross-platform behavior, while testing Windows first.
- [x] Use a terminal-native Textual TUI for the modern UI layer.
- [ ] Decide final app display name and package metadata.

## Release Readiness

- [ ] All planned CLI options work.
- [ ] Direct URL playback works.
- [ ] Search playback works.
- [ ] Clipboard playback works.
- [ ] Last/history playback works.
- [ ] Config persistence works.
- [ ] Cookie handling works.
- [ ] TUI search, history, and settings are usable.
- [ ] Tests pass.
- [ ] Linting passes.
- [ ] Type checking passes or documented exceptions exist.
- [ ] README documents setup, usage, and troubleshooting.
