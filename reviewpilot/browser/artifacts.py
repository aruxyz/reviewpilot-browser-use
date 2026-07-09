from __future__ import annotations

import json
from pathlib import Path

from reviewpilot.core.result import ArtifactPaths, ReviewReport


def save_json_report(report: ReviewReport, artifacts: ArtifactPaths) -> Path | None:
    if artifacts.json_path is None:
        return None
    artifacts.json_path.write_text(
        report.model_dump_json(indent=2), encoding="utf-8"
    )
    return artifacts.json_path


def load_json_report(path: Path) -> ReviewReport:
    data = json.loads(path.read_text(encoding="utf-8"))
    return ReviewReport.model_validate(data)


def write_run_manifest(artifacts: ArtifactPaths, manifest: dict) -> Path:
    manifest_path = artifacts.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path
