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

- [ ] Implement player resolution from configured path.
- [ ] Implement fallback player lookup for `mpv`, `mpvnet.com`, and `mpvnet.exe`.
- [ ] Implement local mpv.net lookup under `%LOCALAPPDATA%\Programs\mpv.net`.
- [ ] Implement URL validation for HTTP/HTTPS URLs.
- [ ] Implement quality/format mapping.
- [ ] Implement size/window argument mapping.
- [ ] Implement audio-only argument handling.
- [ ] Implement loop argument handling.
- [ ] Implement hardware acceleration argument handling.
- [ ] Implement background playback process launch.
- [ ] Implement reverse playlist arguments.
- [ ] Implement subtitle language and no-subtitle handling.
- [ ] Implement custom mpv argument passthrough.
- [ ] Implement dry-run command preview.
- [ ] Add tests for mpv argument generation.
- [ ] Add tests for player resolution ordering.
- [ ] Verify direct URL dry-run playback command.

## Phase 3: Search Parity

- [ ] Implement `yt-dlp` dependency check.
- [ ] Implement YouTube search URL construction.
- [ ] Implement playlist-only search parameter.
- [ ] Implement `yt-dlp` flat-playlist command construction.
- [ ] Implement cookie forwarding to `yt-dlp`.
- [ ] Parse `yt-dlp` tab-separated search rows.
- [ ] Detect result type: Video, Playlist, Channel.
- [ ] Implement result type filtering.
- [ ] Implement max result limiting.
- [ ] Implement `--first` behavior.
- [ ] Implement initial Rich table/basic picker fallback.
- [ ] Add tests for row parsing.
- [ ] Add tests for result type detection.
- [ ] Add tests for filtering.
- [ ] Verify `uv run play "lofi beats" --search --first --dry-run`.

## Phase 4: History, Clipboard, Cookies

- [ ] Implement clipboard text retrieval.
- [ ] Implement history file path.
- [ ] Implement history read/write.
- [ ] Implement history de-dupe by URL.
- [ ] Cap history at 50 entries.
- [ ] Implement replay last history item.
- [ ] Implement interactive history selection.
- [ ] Implement cookie path precedence from config.
- [ ] Implement explicit cookie path validation.
- [ ] Save explicit cookie path to config.
- [ ] Implement default cookie path lookup.
- [ ] Add tests for history de-dupe and cap behavior.
- [ ] Add tests for cookie path precedence.
- [ ] Verify `uv run play --clipboard --dry-run`.
- [ ] Verify `uv run play --last --dry-run`.
- [ ] Verify `uv run play history`.

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
