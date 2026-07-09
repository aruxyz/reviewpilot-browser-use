from __future__ import annotations

import os
import sys
from pathlib import Path

from reviewpilot.github.pr_context import is_running_in_action, load_pr_context


def _action_input(name: str) -> str:
    env = f"INPUT_{name.upper().replace('-', '_')}"
    return os.environ.get(env, "")


def _emit_workflow_command(level: str, message: str) -> None:
    print(f"::{level}::{message}")


def run_action_entrypoint() -> int:
    if not is_running_in_action():
        _emit_workflow_command("error", "reviewpilot-action must run inside a GitHub Action environment.")
        return 2

    preview_url = _action_input("preview-url") or None
    config_path = _action_input("config-path") or ".reviewpilot.yml"
    max_steps = int(_action_input("max-steps") or "30")
    timeout_seconds = int(_action_input("timeout-seconds") or "180")

    try:
        ctx = load_pr_context(preview_url=preview_url)
    except Exception as exc:
        _emit_workflow_command("error", f"Failed to load PR context: {exc}")
        return 2

    from reviewpilot.core.config import ReviewPilotConfig
    from reviewpilot.core.runner import run_review

    config = ReviewPilotConfig()
    config_path_obj = Path(config_path)
    if config_path_obj.exists():
        config = ReviewPilotConfig.from_yaml_file(config_path_obj)

    if preview_url:
        config.app.url = preview_url
    config.review.max_steps = max_steps
    config.review.timeout_seconds = timeout_seconds
    config.output.github_comment = True

    try:
        report = run_review(config, pr_context=ctx)
    except Exception as exc:
        _emit_workflow_command("error", f"ReviewPilot run failed: {exc}")
        return 1

    _emit_workflow_command("notice", f"ReviewPilot status: {report.status.value}")
    print(f"::set-output name=status::{report.status.value}")
    print(f"::set-output name=findings-count::{len(report.all_findings)}")
    return 0


if __name__ == "__main__":
    sys.exit(run_action_entrypoint())
