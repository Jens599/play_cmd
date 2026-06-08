from __future__ import annotations

import subprocess
import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from play_cmd.config import read_config, reset_config, save_config
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
app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Terminal-first mpv and yt-dlp launcher.",
)


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
        typer.Option("--first", help="Play the first search result without a picker."),
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
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without launching.")] = False,
) -> None:
    if ctx.invoked_subcommand is not None:
        return
    if target is None:
        console.print(ctx.get_help())
        raise typer.Exit

    config_data = read_config()
    final_cookie_path = cookie_path or config_data.cookie_path

    if search:
        try:
            results = search_youtube(
                target,
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
        console.print(f"[cyan]Match [{selected.type.value}]:[/cyan] {selected.title}")

    try:
        target_url = validate_http_url(target)
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


@app.command()
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
def history() -> None:
    console.print(f"History is not implemented yet. Planned path: [cyan]{history_path()}[/cyan]")


@app.command()
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
def tui() -> None:
    console.print("Textual TUI is not implemented yet.")


@app.command()
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
    commands = {"config", "history", "search", "tui", "doctor"}
    if args and args[0] not in commands and not args[0].startswith("-"):
        target = args[0]
        trailing = args[1:]
        if any(arg.startswith("-") for arg in trailing):
            app(args=[*trailing, target])
            return

    app(args=args)
