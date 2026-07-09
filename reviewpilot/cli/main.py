from __future__ import annotations

import typer
from rich.console import Console

from reviewpilot.cli.commands.doctor import run_doctor
from reviewpilot.cli.commands.init import run_init
from reviewpilot.cli.commands.report import run_report
from reviewpilot.cli.commands.run import run_run

app = typer.Typer(
    name="reviewpilot",
    help="AI browser QA for every Pull Request, powered by Browser Use.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.command()
def init(
    force: bool = typer.Option(
        False, "--force", help="Overwrite existing .reviewpilot.yml if present."
    ),
) -> None:
    run_init(force=force, console=console)


@app.command()
def run(
    url: str = typer.Option(None, "--url", help="App URL to review (overrides config)."),
    config: str = typer.Option(
        ".reviewpilot.yml", "--config", help="Path to config file."
    ),
    output_dir: str = typer.Option(
        None, "--output-dir", help="Override output directory from config."
    ),
    max_steps: int = typer.Option(
        None, "--max-steps", help="Override max_steps from config."
    ),
    headless: bool = typer.Option(
        True, "--headless/--headed", help="Run browser in headless or headed mode."
    ),
) -> None:
    run_run(
        url=url,
        config_path=config,
        output_dir=output_dir,
        max_steps=max_steps,
        headless=headless,
        console=console,
    )


@app.command()
def report(
    path: str = typer.Option(
        ".reviewpilot-output", "--path", help="Output directory to read reports from."
    ),
    open_browser: bool = typer.Option(
        True, "--open/--no-open", help="Open the HTML report in the default browser."
    ),
) -> None:
    run_report(path=path, open_browser=open_browser, console=console)


@app.command()
def doctor() -> None:
    run_doctor(console=console)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
