from __future__ import annotations

import shutil
from pathlib import Path

from reviewpilot.core.result import ArtifactPaths


def import_screenshots(
    raw_paths: list[str],
    journey_name: str,
    viewport_name: str,
    artifacts: ArtifactPaths,
) -> list[str]:
    if not raw_paths:
        return []
    journey_slug = journey_name.lower().replace(" ", "-").replace("/", "-")
    viewport_slug = viewport_name.lower().replace(" ", "-")
    collected: list[str] = []
    for idx, src in enumerate(raw_paths):
        src_path = Path(src)
        if not src_path.exists() or not src_path.is_file():
            continue
        dest = artifacts.screenshots_dir / f"{journey_slug}-{viewport_slug}-{idx:02d}.png"
        try:
            shutil.copy2(src_path, dest)
            collected.append(str(dest.relative_to(artifacts.output_dir)))
        except (OSError, shutil.SameFileError):
            continue
    return collected
