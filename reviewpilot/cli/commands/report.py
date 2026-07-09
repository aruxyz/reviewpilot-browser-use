from __future__ import annotations

import webbrowser
from pathlib import Path

from rich.console import Console


def run_report(path: str, open_browser: bool, console: Console) -> None:
    output_dir = Path(path)
    html_path = output_dir / "review.html"
    md_path = output_dir / "review.md"
    json_path = output_dir / "review.json"

    if not output_dir.exists():
        console.print(f"[red]Output directory not found:[/red] {output_dir}")
        console.print("Run [bold]reviewpilot run[/bold] first to generate a report.")
        raise SystemExit(1)

    if html_path.exists():
        console.print(f"[green]HTML report:[/green] {html_path}")
        if open_browser:
            try:
                webbrowser.open(html_path.resolve().as_uri())
                console.print("[dim]Opened in default browser.[/dim]")
            except Exception:
                console.print("[yellow]Could not open browser automatically.[/yellow]")
    else:
        console.print(f"[yellow]No HTML report at[/yellow] {html_path}")

    if md_path.exists():
        console.print(f"[green]Markdown report:[/green] {md_path}")
    if json_path.exists():
        console.print(f"[green]JSON report:[/green] {json_path}")
