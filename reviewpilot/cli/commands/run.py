from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.table import Table

from reviewpilot.core.config import ReviewPilotConfig
from reviewpilot.core.runner import run_review
from reviewpilot.core.severity import Severity


def _load_config(config_path: str, url: str | None, output_dir: str | None, max_steps: int | None, headless: bool) -> ReviewPilotConfig:
    path = Path(config_path)
    if path.exists():
        config = ReviewPilotConfig.from_yaml_file(path)
    else:
        config = ReviewPilotConfig()

    if url:
        config.app.url = url
    if output_dir:
        config.output.output_dir = output_dir
    if max_steps:
        config.review.max_steps = max_steps
    config.browser_use.headless = headless

    return config


def _print_summary(report, console: Console) -> None:
    table = Table(title="ReviewPilot Summary", show_header=True, header_style="bold")
    table.add_column("Journey")
    table.add_column("Viewport")
    table.add_column("Status")
    table.add_column("Steps")
    table.add_column("Findings")
    table.add_column("Duration")

    for journey in report.journeys:
        finding_count = len(journey.findings)
        table.add_row(
            journey.name,
            journey.viewport,
            journey.status.value,
            str(journey.steps),
            str(finding_count),
            f"{journey.duration_seconds:.1f}s",
        )

    console.print(table)

    counts = report.counts
    console.print()
    console.print(f"[bold]Overall status:[/bold] {report.status.value}")
    for sev in (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW):
        n = counts[sev]
        if n > 0:
            console.print(f"  {sev.emoji} {sev.value}: {n}")


def run_run(
    url: str | None,
    config_path: str,
    output_dir: str | None,
    max_steps: int | None,
    headless: bool,
    console: Console,
) -> None:
    config = _load_config(config_path, url, output_dir, max_steps, headless)

    if not config.journeys:
        console.print("[red]No journeys configured.[/red] Add journeys to your config file.")
        raise SystemExit(1)

    console.print(f"[bold]ReviewPilot[/bold] — reviewing [cyan]{config.app.url}[/cyan]")
    console.print(f"Journeys: {len(config.journeys)} · Viewports: {len(config.viewports)}")
    console.print()

    try:
        report = run_review(config)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        raise SystemExit(130)
    except Exception as exc:
        console.print(f"[red]Review failed:[/red] {exc}")
        raise SystemExit(1)

    _print_summary(report, console)

    output_path = config.output_path
    console.print()
    console.print(f"[green]Reports saved to[/green] {output_path}/")
    console.print(f"  Markdown: {output_path / 'review.md'}")
    console.print(f"  HTML:     {output_path / 'review.html'}")
    console.print(f"  JSON:     {output_path / 'review.json'}")

    if report.status.value == "passed":
        raise SystemExit(0)
    elif report.status.value == "failed":
        raise SystemExit(1)
    else:
        raise SystemExit(2)
