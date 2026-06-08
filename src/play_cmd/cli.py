from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from play_cmd.config import read_config, reset_config, save_config
from play_cmd.models import AppConfig
from play_cmd.paths import config_path, history_path

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


@app.callback(invoke_without_command=True)
def play(
    ctx: typer.Context,
    target: Annotated[str | None, typer.Argument(help="URL or search query.")] = None,
    search: Annotated[bool, typer.Option("--search", "-s", help="Search YouTube.")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without launching.")] = False,
) -> None:
    if ctx.invoked_subcommand is not None:
        return
    if target is None:
        console.print(ctx.get_help())
        raise typer.Exit

    mode = "search" if search else "direct URL"
    suffix = " dry run" if dry_run else ""
    console.print(
        Panel.fit(
            f"Phase 1 scaffold only: received {mode}{suffix} target\n[cyan]{target}[/cyan]",
            title="play",
            border_style="cyan",
        )
    )


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
def search(query: Annotated[str, typer.Argument(help="YouTube search query.")]) -> None:
    console.print(f"Search is not implemented yet. Query: [cyan]{query}[/cyan]")


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
    app()
