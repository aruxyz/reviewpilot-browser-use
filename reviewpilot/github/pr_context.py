from __future__ import annotations

import json
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class PRContext:
    token: str
    repository: str
    pr_number: int
    head_sha: str
    base_ref: str
    head_ref: str
    preview_url: str | None = None

    @property
    def owner(self) -> str:
        return self.repository.split("/")[0]

    @property
    def repo(self) -> str:
        return self.repository.split("/")[1]


def _read_event_payload() -> dict:
    path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_pr_context(preview_url: str | None = None) -> PRContext:
    token = os.environ.get("INPUT_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set. Pass github-token input or set GITHUB_TOKEN env var.")
    if not repository:
        raise RuntimeError("GITHUB_REPOSITORY is not set. This must run inside a GitHub Action.")

    event = _read_event_payload()
    pr = event.get("pull_request") or {}
    pr_number = int(pr.get("number", 0))
    head_sha = pr.get("head", {}).get("sha") or os.environ.get("GITHUB_SHA", "")
    if not pr_number:
        raise RuntimeError("Could not determine PR number from event payload.")

    base_ref = os.environ.get("GITHUB_BASE_REF", "")
    head_ref = os.environ.get("GITHUB_HEAD_REF", "")

    return PRContext(
        token=token,
        repository=repository,
        pr_number=pr_number,
        head_sha=head_sha,
        base_ref=base_ref,
        head_ref=head_ref,
        preview_url=preview_url,
    )


def is_running_in_action() -> bool:
    return bool(os.environ.get("GITHUB_ACTIONS") == "true")
