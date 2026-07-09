from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from reviewpilot.core.severity import ReviewStatus, Severity


class Finding(BaseModel):
    severity: Severity
    title: str
    page: str = ""
    viewport: str = ""
    journey: str = ""
    expected: str = ""
    actual: str = ""
    why_it_matters: str = ""
    reproduction_steps: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    suggested_fix: str = ""

    @property
    def is_blocking(self) -> bool:
        return self.severity in (Severity.CRITICAL, Severity.HIGH)


class JourneyResult(BaseModel):
    name: str
    goal: str
    url: str | None = None
    viewport: str = ""
    status: ReviewStatus = ReviewStatus.PASSED
    visited_urls: list[str] = Field(default_factory=list)
    actions_taken: list[str] = Field(default_factory=list)
    observations: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    screenshots: list[str] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    final_result: str = ""
    duration_seconds: float = 0.0
    steps: int = 0
    raw_agent_history: dict[str, Any] | None = None

    @property
    def passed(self) -> bool:
        return self.status == ReviewStatus.PASSED


class ReviewReport(BaseModel):
    app_name: str
    app_url: str
    status: ReviewStatus = ReviewStatus.PASSED
    journeys: list[JourneyResult] = Field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""
    total_duration_seconds: float = 0.0

    @property
    def all_findings(self) -> list[Finding]:
        return [f for j in self.journeys for f in j.findings]

    @property
    def findings_by_severity(self) -> dict[Severity, list[Finding]]:
        grouped: dict[Severity, list[Finding]] = {
            Severity.CRITICAL: [],
            Severity.HIGH: [],
            Severity.MEDIUM: [],
            Severity.LOW: [],
        }
        for f in self.all_findings:
            grouped[f.severity].append(f)
        return grouped

    @property
    def counts(self) -> dict[Severity, int]:
        by_sev = self.findings_by_severity
        return {sev: len(items) for sev, items in by_sev.items()}

    @property
    def passed_checks(self) -> list[str]:
        passed: list[str] = []
        for journey in self.journeys:
            if journey.passed and not journey.findings:
                passed.append(journey.name)
        return passed

    def recompute_status(self) -> None:
        if any(j.status == ReviewStatus.ERRORED for j in self.journeys):
            self.status = ReviewStatus.ERRORED
        elif any(f.severity in (Severity.CRITICAL, Severity.HIGH) for f in self.all_findings):
            self.status = ReviewStatus.FAILED
        elif self.all_findings:
            self.status = ReviewStatus.FAILED
        else:
            self.status = ReviewStatus.PASSED


class ArtifactPaths(BaseModel):
    output_dir: Path
    screenshots_dir: Path
    markdown_path: Path | None = None
    html_path: Path | None = None
    json_path: Path | None = None

    @classmethod
    def create(cls, output_dir: Path) -> "ArtifactPaths":
        screenshots_dir = output_dir / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        return cls(
            output_dir=output_dir,
            screenshots_dir=screenshots_dir,
            markdown_path=output_dir / "review.md",
            html_path=output_dir / "review.html",
            json_path=output_dir / "review.json",
        )
