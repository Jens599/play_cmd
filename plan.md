# Start-MPVStream Python Port Plan

## Current PowerShell Behavior

`Start-MPVStream` is a PowerShell module that provides a `play` command for launching online media in `mpv` or `mpv.net`.

Core behavior to preserve:

- Play a direct HTTP/HTTPS URL with `mpv`.
- Search YouTube via `yt-dlp`, then pick a video, playlist, or channel.
- Play the first search result without opening a picker.
- Read a URL from the clipboard.
- Replay the last item or pick from playback history.
- Persist configuration in the user app-data directory.
- Persist recent playback history, de-duplicated and capped at 50 entries.
- Resolve cookies from config, explicit path, default locations, or legacy config.
- Resolve player from configured path, `mpv`, `mpvnet.com`, `mpvnet.exe`, or local mpv.net install.
- Generate `mpv` arguments for size, quality, audio-only, background, loop, hardware acceleration, playlist reverse, subtitles, cookies, and custom args.
- Support dry-run command preview.

Important existing command options:

- `Url` / `u`
- `--size` / `-sz`: `PIP`, `Small`, `Medium`, `Max`
- `--format` / `-f`: `480p`, `720p`, `1080p`, `best`, `audio`
- `--cookie-path` / `-c`
- `--config` / `--cfg`
- `--search` / `-s`
- `--playlist` / `-p`
- `--first` / `-fi`
- `--type` / `-t`: `Video`, `Playlist`, `Channel`
- `--mpv-argument` / `--mpvarg`
- `--dry-run`
- `--clipboard`
- `--history`
- `--last`
- `--audio-only`
- `--loop`
- `--hardware-accel`
- `--background`
- `--reverse-playlist`
- `--no-subtitles`
- `--subtitle-language`
- `--max-results`

## Product Direction

Build a Python app named `play-cmd` that keeps the current terminal-first speed but adds a modern 2026 UI/UX layer.

Recommended direction:

- Keep a fast CLI as the primary automation interface.
- Add a polished terminal UI for search, history, and configuration.
- Do not build a web UI or desktop web shell.
- Design cross-platform behavior, while testing Windows first.

The first Python version should not become a heavy media app. It should remain a launcher and command center for `mpv`, `mpv.net`, and `yt-dlp`.

## Python Stack With uv

Use `uv` for project creation, dependency management, scripts, locking, and execution.

Recommended commands:

```powershell
uv init --app --package play-cmd
uv python pin 3.13
uv add typer rich textual pydantic platformdirs pyperclip
uv add --dev ruff pytest pytest-cov mypy pyinstaller
uv lock
uv run play --help
```

Recommended runtime dependencies:

- `typer`: modern CLI with typed options and shell completion support.
- `rich`: beautiful CLI output, tables, panels, progress, tracebacks.
- `textual`: modern terminal UI for search, history, and settings.
- `pydantic`: validated config and structured models.
- `platformdirs`: correct per-OS app-data paths.
- `pyperclip`: clipboard access.

Recommended dev dependencies:

- `ruff`: linting and formatting.
- `pytest`: tests.
- `pytest-cov`: coverage.
- `mypy`: static type checking.
- `pyinstaller`: optional single-file executable builds.

Potential later dependencies:

- `watchfiles`: reactive refresh for config/history UI.

## Proposed Project Structure

```text
play_cmd/
  pyproject.toml
  uv.lock
  README.md
  plan.md
  src/
    play_cmd/
      __init__.py
      __main__.py
      cli.py
      app.py
      config.py
      cookies.py
      history.py
      mpv.py
      search.py
      models.py
      paths.py
      clipboard.py
      tui/
        __init__.py
        search_app.py
        history_app.py
        settings_app.py
        theme.py
  tests/
    test_mpv_args.py
    test_search_parse.py
    test_config.py
    test_history.py
```

Module responsibilities:

- `cli.py`: Typer commands and option parsing.
- `app.py`: orchestration equivalent to `Start-MPVStream`.
- `config.py`: load, save, validate, reset settings.
- `cookies.py`: cookie path resolution and validation.
- `history.py`: history read/write, last item, de-dupe, cap at 50.
- `mpv.py`: player resolution, argument building, process launch.
- `search.py`: `yt-dlp` search command, row parsing, filtering.
- `models.py`: Pydantic models for config, search results, history items.
- `paths.py`: app data paths via `platformdirs`.
- `clipboard.py`: clipboard retrieval.
- `tui/*`: Textual screens for high-polish interactions.

## CLI Design

Primary command:

```powershell
uv run play <url-or-query> [options]
```

Console script in `pyproject.toml`:

```toml
[project.scripts]
play = "play_cmd.cli:main"
```

Example commands:

```powershell
uv run play "https://youtu.be/dQw4w9WgXcQ"
uv run play "lofi beats" --search
uv run play "lofi beats" --search --first
uv run play --clipboard
uv run play --last
uv run play --history
uv run play config
uv run play tui
```

Recommended subcommands:

- `play`: default playback/search flow.
- `play config`: interactive or direct config editing.
- `play history`: history picker or printed history table.
- `play search QUERY`: explicit search mode.
- `play tui`: full-screen Textual app.
- `play doctor`: dependency and environment diagnostics.

CLI compatibility should be close to PowerShell, but Python option names should use conventional kebab-case. Short aliases can preserve muscle memory.

## Modern 2026 UI/UX Direction

Use a two-layer UX:

- Rich CLI for quick commands and readable output.
- Textual TUI for immersive search, history, config, and diagnostics.

Visual language:

- Dark-first, high-contrast interface.
- Command-palette interaction model.
- Dense but legible media cards.
- Keyboard-first navigation with visible shortcuts.
- Minimal chrome, strong focus states, and fast transitions.
- Accent colors that communicate state: cyan for active, green for playable, amber for warnings, red for errors.

Search TUI should include:

- Top command/search bar with query, filters, and result count.
- Left rail for source/filter chips: Videos, Playlists, Channels, Audio, Recent.
- Main result list with title, type, duration, uploader, views, and URL.
- Preview/details pane for selected result.
- Footer shortcut bar: Enter Play, A Audio, F Format, S Size, C Copy URL, D Dry Run, Esc Back.
- Empty, loading, and error states that are informative instead of plain text failures.

History TUI should include:

- Chronological grouped list: Today, Yesterday, This Week, Older.
- Fast fuzzy filtering.
- One-key replay.
- Delete single item and clear history confirmations.
- Type badges for Direct, Search, Video, Playlist, Channel.

Settings TUI should include:

- Form-like controls for player path, cookie path, size, quality, subtitles, and toggles.
- Inline validation for missing files and invalid values.
- Dependency status cards for `mpv`, `mpv.net`, `yt-dlp`, and cookies.
- Save/reset flows with explicit confirmation.

Doctor UX should include:

- A table of checks with status, detected path/version, and fix hints.
- Suggested install commands for missing dependencies.
- A copyable diagnostics summary.

## Config Model

Use `platformdirs.user_config_dir("play-cmd")` or `platformdirs.user_config_path("play-cmd")`.

Recommended config path:

```text
%APPDATA%\play-cmd\config.json
```

Recommended history path:

```text
%APPDATA%\play-cmd\history.json
```

Initial config fields:

```json
{
  "cookie_path": null,
  "player_path": null,
  "default_size": "PIP",
  "default_format": "480p",
  "max_results": 10,
  "audio_only": false,
  "background": false,
  "loop": false,
  "hardware_accel": false,
  "reverse_playlist": false,
  "no_subtitles": false,
  "subtitle_language": ["en"],
  "theme": "neon-dark"
}
```

Start fresh with a new Python config/history store. Do not import legacy PowerShell config or history in v1.

## mpv Argument Mapping

Preserve existing quality mapping:

```python
FORMAT_MAP = {
    "480p": "bestvideo[height<=480]+bestaudio/best",
    "720p": "bestvideo[height<=720]+bestaudio/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best",
    "best": "bestvideo+bestaudio/best",
    "audio": "bestaudio/best",
}
```

Preserve size mapping:

- `PIP`: `--geometry=320x180-10-10`, `--autofit=320x180`, `--no-border`, `--ontop`
- `Small`: `--geometry=854x480-10-10`, `--autofit=854x480`
- `Medium`: `--geometry=1280x720-10-10`, `--autofit=1280x720`
- `Max`: `--fullscreen`

Recommended implementation detail:

- Use `subprocess.run([...], check=True)` for foreground playback.
- Use `subprocess.Popen([...], start_new_session=True)` for background playback.
- Avoid shell command strings; pass argument lists directly.
- In dry-run mode, print a shell-escaped preview with `shlex.join` where available, with Windows-safe fallback if needed.

## Search Implementation

Use `yt-dlp` in flat playlist mode, preserving the current output columns:

```text
%(title)s\t%(id)s\t%(ie_key)s\t%(webpage_url)s\t%(duration_string)s\t%(uploader)s\t%(view_count)s
```

Search URL behavior:

- Base: `https://www.youtube.com/results?search_query=<encoded-query>`
- Playlist-only: append `&sp=EgIQAw%3D%3D`
- Limit with `--playlist-items 1:<max-results>`
- Add `--cookies <path>` when available.

Result typing:

- Playlist if URL contains `/playlist?list=`, ID starts with `PL` or `UU`.
- Channel if URL indicates channel/user/handle, ID starts with `UC`, or `ie_key` is `YoutubeTab`.
- Otherwise Video.

## Implementation Phases

### Phase 1: uv Scaffold and Core CLI

- Initialize the Python app with `uv`.
- Add dependencies and dev tools.
- Create Typer CLI with `play`, `config`, `history`, `search`, `doctor` placeholders.
- Add Pydantic models.
- Add path helpers.
- Add config load/save/reset.
- Add tests for config defaults.

Verification:

```powershell
uv run play --help
uv run pytest
uv run ruff check .
```

### Phase 2: mpv Playback Parity

- Implement player resolution.
- Implement argument generation.
- Implement URL validation.
- Implement dry-run.
- Implement foreground/background process launch.
- Add tests for argument generation.

Verification:

```powershell
uv run play "https://youtu.be/dQw4w9WgXcQ" --dry-run
uv run pytest tests/test_mpv_args.py
```

### Phase 3: Search Parity

- Implement `yt-dlp` dependency checks.
- Implement YouTube search command construction.
- Implement row parsing and type filtering.
- Implement `--first`.
- Implement Rich table picker fallback before Textual is built.
- Add tests for row parsing and filtering.

Verification:

```powershell
uv run play "lofi beats" --search --first --dry-run
uv run pytest tests/test_search_parse.py
```

### Phase 4: History, Clipboard, Cookies

- Implement clipboard URL retrieval.
- Implement history add/read/last/select.
- Implement cookie path resolution.
- Add config save when explicit cookie path is provided.
- Add tests for history de-dupe and cap behavior.

Verification:

```powershell
uv run play --clipboard --dry-run
uv run play --last --dry-run
uv run play history
uv run pytest
```

### Phase 5: Modern TUI

- Build Textual search screen.
- Build Textual history screen.
- Build Textual settings screen.
- Build shared theme and shortcuts.
- Integrate TUI picker into CLI search/history flows.
- Keep non-interactive flags working for automation.

Verification:

```powershell
uv run play tui
uv run play "lofi beats" --search
```

### Phase 6: Doctor, Polish, Packaging

- Implement `play doctor`.
- Add shell completion instructions.
- Add README usage examples.
- Add `pyinstaller` build target if wanted.
- Add GitHub-ready CI commands if this becomes a repo.

Verification:

```powershell
uv run play doctor
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest --cov=play_cmd
```

## Testing Strategy

Prioritize tests around pure logic first:

- Config defaults, validation, save/load.
- mpv argument mapping.
- player candidate ordering.
- yt-dlp row parsing.
- result type detection.
- history de-dupe and 50-item cap.
- cookie path precedence.

Avoid requiring real `mpv` or `yt-dlp` in unit tests. Mock subprocess calls.

Add integration tests later for machines that have `mpv` and `yt-dlp` installed.

## Risks and Decisions

Known risks:

- `yt-dlp` output can change or include missing fields.
- `mpv.net` process behavior differs from `mpv` on Windows.
- Clipboard behavior varies by platform and session type.
- Textual UI should not block simple automation flows.
- Background playback needs careful process handling on Windows.

Implementation decisions:

- Use `play` as the installed command.
- Start fresh with Python config/history; do not import legacy PowerShell data in v1.
- Do not build a web UI or desktop web shell.
- `doctor` should print install instructions instead of installing dependencies automatically.
- Design cross-platform behavior, while testing Windows first.
- Use a terminal-native Textual TUI for the modern UI layer.

## Recommended First Milestone

The best first milestone is a tested CLI with playback, dry-run, config, search-first, history, clipboard, and doctor. Build the Textual UI after the core behavior is reliable.

Milestone target:

```powershell
uv run play "https://youtu.be/dQw4w9WgXcQ" --dry-run
uv run play "lofi beats" --search --first --dry-run
uv run play --clipboard --dry-run
uv run play --last --dry-run
uv run play doctor
uv run pytest
```
