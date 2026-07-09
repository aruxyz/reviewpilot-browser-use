from __future__ import annotations

import os
import shutil
import sys

from rich.console import Console
from rich.table import Table


def _check_python_version(console: Console) -> bool:
    ok = sys.version_info >= (3, 10)
    status = "[green]OK[/green]" if ok else "[red]FAIL[/red]"
    console.print(f"  Python >= 3.10  {status}  ({sys.version.split()[0]})")
    return ok


def _check_import(name: str, console: Console) -> bool:
    try:
        __import__(name)
        console.print(f"  {name:25s}  [green]OK[/green]")
        return True
    except ImportError as exc:
        console.print(f"  {name:25s}  [red]FAIL[/red]  ({exc})")
        return False


def _check_env_var(name: str, console: Console) -> bool:
    value = os.environ.get(name, "")
    if value:
        masked = value[:4] + "..." if len(value) > 4 else "set"
        console.print(f"  {name:25s}  [green]OK[/green]  ({masked})")
        return True
    console.print(f"  {name:25s}  [yellow]NOT SET[/yellow]")
    return False


def _check_browser(console: Console) -> bool:
    chrome = shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium")
    if chrome:
        console.print(f"  Chrome/Chromium            [green]OK[/green]  ({chrome})")
        return True
    console.print("  Chrome/Chromium            [yellow]NOT FOUND on PATH[/yellow]")
    console.print("    [dim]Browser Use will download Chromium on first run via Playwright.[/dim]")
    return True


def run_doctor(console: Console) -> None:
    console.print("[bold]ReviewPilot Doctor[/bold]\n")

    console.print("[bold]Environment:[/bold]")
    results = []
    results.append(_check_python_version(console))

    console.print("\n[bold]Python packages:[/bold]")
    for pkg in ["browser_use", "typer", "rich", "pydantic", "yaml", "jinja2", "github"]:
        results.append(_check_import(pkg, console))

    console.print("\n[bold]Browser:[/bold]")
    results.append(_check_browser(console))

    console.print("\n[bold]API keys (LLM providers):[/bold]")
    any_key = False
    for var in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "BROWSER_USE_API_KEY"]:
        if _check_env_var(var, console):
            any_key = True

    console.print()
    if not any_key:
        console.print("[yellow]No LLM API key found.[/yellow] Set at least one of:")
        console.print("  export OPENAI_API_KEY=sk-...")
        console.print("  export ANTHROPIC_API_KEY=sk-ant-...")
        console.print("  export GOOGLE_API_KEY=...")
        console.print("  export BROWSER_USE_API_KEY=bu-...")

    if all(results):
        console.print("\n[green]All checks passed.[/green] You're ready to run ReviewPilot.")
    else:
        console.print("\n[yellow]Some checks failed.[/yellow] Fix the issues above before running.")
        raise SystemExit(1)
