from __future__ import annotations

from rich.console import Console

from reviewpilot.core.config import DEFAULT_CONFIG_YAML
from reviewpilot.core.config import ReviewPilotConfig

DEFAULT_CONFIG_PATH = ".reviewpilot.yml"


def run_init(force: bool, console: Console) -> None:
    from pathlib import Path

    config_path = Path(DEFAULT_CONFIG_PATH)
    if config_path.exists() and not force:
        console.print(
            f"[yellow]Config file already exists at {config_path}.[/yellow] "
            "Use --force to overwrite."
        )
        raise SystemExit(1)

    config_path.write_text(DEFAULT_CONFIG_YAML, encoding="utf-8")
    console.print(f"[green]Created[/green] {config_path}")
    console.print(
        "Edit it to set your app URL, journeys, and viewports, then run:\n"
        "  [bold]reviewpilot run --config .reviewpilot.yml[/bold]"
    )
