from __future__ import annotations

import json
from typing import Any

from reviewpilot.browser.browser_use_runner import LLMFactory
from reviewpilot.core.severity import ReviewStatus, Severity
from reviewpilot.judge.prompts import build_judge_prompt
from reviewpilot.judge.schemas import FindingSchema, JourneyJudgement


def _parse_json_from_text(text: str) -> dict[str, Any] | None:
    fenced = _extract_fenced_json(text)
    if fenced is not None:
        return fenced
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start : i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    return None
    return None


def _extract_fenced_json(text: str) -> dict[str, Any] | None:
    marker = "```json"
    idx = text.find(marker)
    if idx == -1:
        marker = "```"
        idx = text.find(marker)
        if idx == -1:
            return None
    start = idx + len(marker)
    end = text.find("```", start)
    if end == -1:
        return None
    payload = text[start:end].strip()
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return None


def _coerce_severity(value: str) -> Severity:
    try:
        return Severity(value.lower().strip())
    except ValueError:
        return Severity.LOW


def _coerce_status(value: str) -> ReviewStatus:
    try:
        return ReviewStatus(value.lower().strip())
    except ValueError:
        return ReviewStatus.PASSED


class JudgeEvaluator:
    def __init__(self, model: str):
        self._llm = LLMFactory.build(model)

    async def judge(
        self,
        journey_name: str,
        journey_goal: str,
        viewport: str,
        browser_result: dict[str, Any],
    ) -> JourneyJudgement:
        prompt = build_judge_prompt(journey_name, journey_goal, viewport, browser_result)
        try:
            response = await self._llm.ainvoke(prompt)
            text = response.content if hasattr(response, "content") else str(response)
            parsed = _parse_json_from_text(text)
            if parsed is None:
                return _degraded_judgement(
                    journey_name, browser_result, "Judge returned non-JSON output"
                )
            return _build_judgement(parsed)
        except Exception as exc:
            return _degraded_judgement(journey_name, browser_result, f"Judge call failed: {exc}")


def _build_judgement(parsed: dict[str, Any]) -> JourneyJudgement:
    findings_raw = parsed.get("findings") or []
    findings: list[FindingSchema] = []
    for raw in findings_raw:
        if not isinstance(raw, dict):
            continue
        findings.append(
            FindingSchema(
                severity=raw.get("severity", "low"),
                title=raw.get("title", "Untitled finding"),
                page=raw.get("page", ""),
                viewport=raw.get("viewport", ""),
                expected=raw.get("expected", ""),
                actual=raw.get("actual", ""),
                why_it_matters=raw.get("why_it_matters", ""),
                reproduction_steps=raw.get("reproduction_steps") or [],
                evidence=raw.get("evidence") or [],
                suggested_fix=raw.get("suggested_fix", ""),
            )
        )
    return JourneyJudgement(
        summary=parsed.get("summary", ""),
        status=parsed.get("status", "passed"),
        findings=findings,
        passed_checks=parsed.get("passed_checks") or [],
    )


def _degraded_judgement(
    journey_name: str, browser_result: dict[str, Any], reason: str
) -> JourneyJudgement:
    errors = browser_result.get("errors") or []
    has_errors = bool(errors)
    return JourneyJudgement(
        summary=f"Judge could not produce a structured judgement for '{journey_name}'. {reason}.",
        status="errored" if has_errors else "failed",
        findings=[],
        passed_checks=[],
    )


def judgement_to_findings(judgement: JourneyJudgement) -> list:
    from reviewpilot.core.result import Finding

    return [
        Finding(
            severity=_coerce_severity(f.severity),
            title=f.title,
            page=f.page,
            viewport=f.viewport,
            expected=f.expected,
            actual=f.actual,
            why_it_matters=f.why_it_matters,
            reproduction_steps=f.reproduction_steps,
            evidence=f.evidence,
            suggested_fix=f.suggested_fix,
        )
        for f in judgement.findings
    ]


def judgement_to_status(judgement: JourneyJudgement) -> ReviewStatus:
    return _coerce_status(judgement.status)
