from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from reviewpilot.browser.artifacts import save_json_report, write_run_manifest
from reviewpilot.browser.browser_use_runner import BrowserUseRunner
from reviewpilot.browser.screenshots import import_screenshots
from reviewpilot.core.config import ReviewPilotConfig
from reviewpilot.core.result import ArtifactPaths, JourneyResult, ReviewReport
from reviewpilot.core.severity import ReviewStatus
from reviewpilot.judge.evaluator import (
    JudgeEvaluator,
    judgement_to_findings,
    judgement_to_status,
)
from reviewpilot.reports.html import write_html_report
from reviewpilot.reports.markdown import generate_markdown_report

if TYPE_CHECKING:
    from reviewpilot.github.pr_context import PRContext


def _resolve_viewports_for_journey(journey_viewport: str | None, config: ReviewPilotConfig):
    if journey_viewport is not None:
        for v in config.viewports:
            if v.name == journey_viewport:
                return [v]
        raise ValueError(f"Journey references unknown viewport '{journey_viewport}'")
    return config.viewports


async def _run_single_journey(
    runner: BrowserUseRunner,
    judge: JudgeEvaluator,
    config: ReviewPilotConfig,
    journey,
    viewport,
) -> JourneyResult:
    max_steps = journey.max_steps or config.review.max_steps
    timeout_seconds = journey.timeout_seconds or config.review.timeout_seconds

    start = time.monotonic()
    browser_result = await runner.run_journey(
        journey=journey,
        app_url=config.app.url,
        viewport=viewport,
        max_steps=max_steps,
        timeout_seconds=timeout_seconds,
    )
    duration = time.monotonic() - start

    if browser_result.get("status") == "skipped":
        return JourneyResult(
            name=journey.name,
            goal=journey.goal,
            viewport=viewport.name,
            status=ReviewStatus.SKIPPED,
            duration_seconds=duration,
        )

    artifacts = ArtifactPaths.create(config.output_path)
    screenshots = import_screenshots(
        raw_paths=browser_result.get("screenshot_paths") or [],
        journey_name=journey.name,
        viewport_name=viewport.name,
        artifacts=artifacts,
    )

    judgement = await judge.judge(
        journey_name=journey.name,
        journey_goal=journey.goal,
        viewport=viewport.name,
        browser_result=browser_result,
    )

    findings = judgement_to_findings(judgement)
    for f in findings:
        f.journey = journey.name
        if not f.viewport:
            f.viewport = viewport.name

    status = judgement_to_status(judgement)
    if browser_result.get("errors") and status == ReviewStatus.PASSED:
        status = ReviewStatus.FAILED

    return JourneyResult(
        name=journey.name,
        goal=journey.goal,
        url=journey.url or config.app.url,
        viewport=viewport.name,
        status=status,
        visited_urls=browser_result.get("urls") or [],
        actions_taken=browser_result.get("actions") or [],
        observations=[],
        errors=browser_result.get("errors") or [],
        screenshots=screenshots,
        findings=findings,
        final_result=browser_result.get("final_result") or judgement.summary,
        duration_seconds=duration,
        steps=browser_result.get("steps") or 0,
    )


async def _run_review_async(config: ReviewPilotConfig, pr_context: "PRContext | None") -> ReviewReport:
    output_path = config.output_path
    output_path.mkdir(parents=True, exist_ok=True)
    artifacts = ArtifactPaths.create(output_path)

    runner = BrowserUseRunner(config.browser_use, output_path)
    judge = JudgeEvaluator(config.browser_use.task_model)

    journey_results: list[JourneyResult] = []
    for journey in config.journeys:
        viewports = _resolve_viewports_for_journey(journey.viewport, config)
        for viewport in viewports:
            result = await _run_single_journey(runner, judge, config, journey, viewport)
            journey_results.append(result)

    report = ReviewReport(
        app_name=config.app.name,
        app_url=config.app.url,
        journeys=journey_results,
        started_at=datetime.now(timezone.utc).isoformat(),
        finished_at=datetime.now(timezone.utc).isoformat(),
        total_duration_seconds=sum(j.duration_seconds for j in journey_results),
    )
    report.recompute_status()

    if config.output.markdown and artifacts.markdown_path:
        markdown = generate_markdown_report(report)
        artifacts.markdown_path.write_text(markdown, encoding="utf-8")

    if config.output.html and artifacts.html_path:
        write_html_report(report, artifacts.html_path)

    if artifacts.json_path:
        save_json_report(report, artifacts)

    write_run_manifest(
        artifacts,
        {
            "app": config.app.name,
            "url": config.app.url,
            "journeys": len(journey_results),
            "status": report.status.value,
            "started_at": report.started_at,
            "finished_at": report.finished_at,
        },
    )

    if config.output.github_comment and pr_context is not None:
        _post_to_github(report, pr_context)

    return report


def _post_to_github(report: ReviewReport, pr_context: "PRContext") -> None:
    from reviewpilot.github.comments import upsert_pr_comment
    from reviewpilot.reports.markdown import generate_markdown_report

    markdown = generate_markdown_report(report)
    upsert_pr_comment(pr_context, markdown)


def run_review(
    config: ReviewPilotConfig,
    pr_context: "PRContext | None" = None,
) -> ReviewReport:
    return asyncio.run(_run_review_async(config, pr_context))


async def run_review_async(
    config: ReviewPilotConfig,
    pr_context: "PRContext | None" = None,
) -> ReviewReport:
    return await _run_review_async(config, pr_context)
