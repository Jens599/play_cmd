from __future__ import annotations

import subprocess
import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from play_cmd.clipboard import ClipboardError, read_clipboard_text
from play_cmd.config import read_config, reset_config, save_config
from play_cmd.cookies import CookiePathError, resolve_cookie_path
from play_cmd.history import last_history_item, read_history, record_playback
from play_cmd.models import AppConfig, ResultType, SearchResult, StreamFormat, WindowSize
from play_cmd.mpv import (
    PlaybackOptions,
    PlayerNotFoundError,
    build_mpv_args,
    launch_player,
    preview_command,
    require_player,
    validate_http_url,
)
from play_cmd.paths import config_path, history_path
from play_cmd.search import SearchError, YtdlpNotFoundError, search_youtube

console = Console()
COMMANDS = {"config", "history", "search", "tui", "doctor"}
app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Terminal-first mpv and yt-dlp launcher.",
)
command_app = typer.Typer(add_completion=False, no_args_is_help=True)


def normalize_root_args(args: list[str]) -> list[str]:
    if any(arg in COMMANDS for arg in args):
        return args

    target_index: int | None = None
    skip_next = False
    value_options = {
        "--size",
        "-sz",
        "--format",
        "-f",
        "--cookie-path",
        "-c",
        "--type",
        "-t",
        "--max-results",
        "--subtitle-language",
        "--mpv-argument",
    }

    for index, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg in value_options:
            skip_next = True
            continue
        if arg.startswith("-"):
            continue
        target_index = index
        break

    if target_index is None or target_index == len(args) - 1:
        return args

    return [*args[:target_index], *args[target_index + 1 :], args[target_index]]


def print_config(config: AppConfig) -> None:
    table = Table(title="play config", show_header=True, header_style="bold cyan")
    table.add_column("Setting")
    table.add_column("Value")
    for key, value in config.model_dump(mode="json").items():
        table.add_row(key, str(value))
    console.print(table)


def select_search_result(results: list[SearchResult], title: str) -> SearchResult | None:
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("No", justify="right")
    table.add_column("Type")
    table.add_column("Length")
    table.add_column("Views", justify="right")
    table.add_column("Uploader")
    table.add_column("Title")
    for index, result in enumerate(results, start=1):
        table.add_row(
            str(index),
            result.type.value,
            result.duration or "-",
            str(result.view_count or "-"),
            result.uploader or "-",
            result.title,
        )
    console.print(table)

    answer = typer.prompt("Select number or press Enter to cancel", default="", show_default=False)
    if not answer.strip():
        return None
    try:
        selected_index = int(answer)
    except ValueError:
        console.print("[red]Invalid selection.[/red]")
        return None
    if selected_index < 1 or selected_index > len(results):
        console.print("[red]Invalid selection.[/red]")
        return None
    return results[selected_index - 1]


def select_history_item(title: str = "Playback History") -> str | None:
    items = read_history()
    if not items:
        console.print(f"[yellow]No history found at {history_path()}[/yellow]")
        return None

    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("No", justify="right")
    table.add_column("Type")
    table.add_column("Played")
    table.add_column("Title")
    table.add_column("URL")
    for index, item in enumerate(items, start=1):
        table.add_row(
            str(index),
            item.type.value,
            item.played_at.strftime("%Y-%m-%d %H:%M"),
            item.title,
            item.url,
        )
    console.print(table)

    answer = typer.prompt("Select number or press Enter to cancel", default="", show_default=False)
    if not answer.strip():
        return None
    try:
        selected_index = int(answer)
    except ValueError:
        console.print("[red]Invalid selection.[/red]")
        return None
    if selected_index < 1 or selected_index > len(items):
        console.print("[red]Invalid selection.[/red]")
        return None
    return items[selected_index - 1].url


@app.callback(invoke_without_command=True)
def play(
    ctx: typer.Context,
    target: Annotated[str | None, typer.Argument(help="URL or search query.")] = None,
    size: Annotated[
        WindowSize | None,
        typer.Option("--size", "-sz", help="Window size preset."),
    ] = None,
    ytdl_format: Annotated[
        StreamFormat | None,
        typer.Option("--format", "-f", help="yt-dlp format preset."),
    ] = None,
    cookie_path: Annotated[
        str | None,
        typer.Option("--cookie-path", "-c", help="Path to cookies.txt."),
    ] = None,
    search: Annotated[bool, typer.Option("--search", "-s", help="Search YouTube.")] = False,
    playlist: Annotated[
        bool,
        typer.Option("--playlist", "-p", help="Search for playlists only."),
    ] = False,
    first: Annotated[
        bool,
        typer.Option("--first", "-fi", help="Play the first search result without a picker."),
    ] = False,
    result_type: Annotated[
        ResultType | None,
        typer.Option("--type", "-t", help="Filter search results by type."),
    ] = None,
    max_results: Annotated[
        int | None,
        typer.Option("--max-results", help="Number of search results, from 1 to 50."),
    ] = None,
    audio_only: Annotated[
        bool | None,
        typer.Option("--audio-only", "-a", help="Stream audio only."),
    ] = None,
    background: Annotated[
        bool | None,
        typer.Option("--background", "-b", help="Run player in background."),
    ] = None,
    loop: Annotated[bool | None, typer.Option("--loop", "-l", help="Loop playback.")] = None,
    hardware_accel: Annotated[
        bool | None,
        typer.Option("--hardware-accel", help="Enable hardware acceleration."),
    ] = None,
    reverse_playlist: Annotated[
        bool | None,
        typer.Option("--reverse-playlist", "-r", help="Reverse playlist playback order."),
    ] = None,
    no_subtitles: Annotated[
        bool | None,
        typer.Option("--no-subtitles", help="Disable subtitle language preference."),
    ] = None,
    subtitle_language: Annotated[
        list[str] | None,
        typer.Option("--subtitle-language", help="Preferred subtitle language."),
    ] = None,
    mpv_argument: Annotated[
        list[str] | None,
        typer.Option("--mpv-argument", help="Extra mpv argument appended to launch."),
    ] = None,
    clipboard: Annotated[
        bool,
        typer.Option("--clipboard", help="Read the target URL from the clipboard."),
    ] = False,
    last: Annotated[
        bool,
        typer.Option("--last", help="Replay the most recent history item."),
    ] = False,
    history_pick: Annotated[
        bool,
        typer.Option("--history", help="Pick a target from playback history."),
    ] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without launching.")] = False,
) -> None:
    if ctx.invoked_subcommand is not None:
        return
    source_count = sum([target is not None, clipboard, last, history_pick])
    if source_count == 0:
        console.print(ctx.get_help())
        raise typer.Exit
    if source_count > 1:
        console.print(
            "[red]Choose only one target source: target, --clipboard, --last, or --history.[/red]"
        )
        raise typer.Exit(code=2)

    config_data = read_config()
    try:
        final_cookie_path, should_save_cookie_path = resolve_cookie_path(
            cookie_path,
            config_data.cookie_path,
            save_explicit=True,
        )
    except CookiePathError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=2) from error

    if should_save_cookie_path and final_cookie_path != config_data.cookie_path:
        config_data.cookie_path = final_cookie_path
        save_config(config_data)
        console.print(f"[green]Saved cookie path:[/green] {final_cookie_path}")

    history_title: str | None = None
    history_type = ResultType.direct

    if clipboard:
        try:
            target = read_clipboard_text()
        except ClipboardError as error:
            console.print(f"[red]{error}[/red]")
            raise typer.Exit(code=1) from error
    elif last:
        item = last_history_item()
        if item is None:
            console.print(f"[yellow]No history found at {history_path()}[/yellow]")
            raise typer.Exit(code=1)
        target = item.url
        history_title = item.title
        history_type = item.type
    elif history_pick:
        target = select_history_item()
        if target is None:
            raise typer.Exit

    if search:
        try:
            results = search_youtube(
                target or "",
                max_results=max_results or config_data.max_results,
                playlist=playlist,
                cookie_path=final_cookie_path,
                result_type=result_type,
            )
        except YtdlpNotFoundError as error:
            console.print(f"[red]{error}[/red]")
            raise typer.Exit(code=1) from error
        except SearchError as error:
            console.print(f"[red]Search failed: {error}[/red]")
            raise typer.Exit(code=1) from error

        if not results:
            console.print("[yellow]No search results found.[/yellow]")
            raise typer.Exit(code=1)

        selected = (
            results[0] if first else select_search_result(results, f"Search Results: {target}")
        )
        if selected is None:
            raise typer.Exit
        target = selected.url
        history_title = selected.title
        history_type = selected.type
        console.print(f"[cyan]Match [{selected.type.value}]:[/cyan] {selected.title}")

    try:
        target_url = validate_http_url(target or "")
    except ValueError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=2) from error

    options = PlaybackOptions(
        size=size or config_data.default_size,
        ytdl_format=ytdl_format or config_data.default_format,
        cookie_path=final_cookie_path,
        audio_only=config_data.audio_only if audio_only is None else audio_only,
        background=config_data.background if background is None else background,
        loop=config_data.loop if loop is None else loop,
        hardware_accel=config_data.hardware_accel if hardware_accel is None else hardware_accel,
        reverse_playlist=(
            config_data.reverse_playlist if reverse_playlist is None else reverse_playlist
        ),
        no_subtitles=config_data.no_subtitles if no_subtitles is None else no_subtitles,
        subtitle_language=subtitle_language or config_data.subtitle_language,
        custom_args=mpv_argument or [],
    )
    mpv_args = build_mpv_args(options)

    try:
        player = require_player(config_data.player_path)
    except PlayerNotFoundError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    command = [player.command, *mpv_args, target_url]
    console.print("[green]Launching:[/green]")
    console.print(f"  [yellow]{preview_command(command)}[/yellow]")

    if dry_run:
        console.print("[cyan]Dry run: player was not started.[/cyan]")
        return

    try:
        launch_player(player, [*mpv_args, target_url], background=options.background)
    except OSError as error:
        console.print(f"[red]Failed to start player: {error}[/red]")
        raise typer.Exit(code=1) from error
    except subprocess.CalledProcessError as error:
        console.print(f"[red]Player exited with code {error.returncode}.[/red]")
        raise typer.Exit(code=1) from error

    if options.background:
        console.print("[green]Player started in background.[/green]")

    record_playback(target_url, title=history_title, result_type=history_type)


@app.command()
@command_app.command()
def config(
    show: Annotated[bool, typer.Option("--show", help="Show current config.")] = True,
    reset: Annotated[bool, typer.Option("--reset", help="Reset config to defaults.")] = False,
) -> None:
    if reset:
        current = reset_config()
        console.print(f"[green]Reset config:[/green] {config_path()}")
    else:
        current = read_config()
        if not config_path().exists():
            save_config(current)
            console.print(f"[green]Created config:[/green] {config_path()}")

    if show:
        print_config(current)


@app.command()
@command_app.command()
def history() -> None:
    select_history_item()


@app.command()
@command_app.command()
def search(
    query: Annotated[str, typer.Argument(help="YouTube search query.")],
    playlist: Annotated[
        bool,
        typer.Option("--playlist", "-p", help="Search for playlists only."),
    ] = False,
    result_type: Annotated[
        ResultType | None,
        typer.Option("--type", "-t", help="Filter search results by type."),
    ] = None,
    max_results: Annotated[int, typer.Option("--max-results", help="Number of results.")] = 10,
) -> None:
    try:
        results = search_youtube(
            query,
            max_results=max_results,
            playlist=playlist,
            result_type=result_type,
        )
    except YtdlpNotFoundError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error
    except SearchError as error:
        console.print(f"[red]Search failed: {error}[/red]")
        raise typer.Exit(code=1) from error

    if not results:
        console.print("[yellow]No search results found.[/yellow]")
        return
    select_search_result(results, f"Search Results: {query}")


@app.command()
@command_app.command()
def tui() -> None:
    console.print("Textual TUI is not implemented yet.")


@app.command()
@command_app.command()
def doctor() -> None:
    table = Table(title="play doctor", show_header=True, header_style="bold cyan")
    table.add_column("Check")
    table.add_column("Status")
    table.add_row("Config path", str(config_path()))
    table.add_row("History path", str(history_path()))
    table.add_row("Dependency checks", "Phase 6")
    console.print(table)


def main() -> None:
    args = sys.argv[1:]
    if args and args[0] in COMMANDS:
        command_app(args=args)
        return
    app(args=normalize_root_args(args))
