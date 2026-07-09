from __future__ import annotations

import json
from typing import Any

from browser_use.llm.messages import UserMessage

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
    idx = text.find("```")
    if idx == -1:
        return None
    start = idx + 3
    newline = text.find("\n", start)
    if newline != -1:
        start = newline + 1
    end = text.find("```", start)
    if end == -1:
        return None
    payload = text[start:end].strip()
    json_start = payload.find("{")
    if json_start == -1:
        return None
    json_end = payload.rfind("}")
    if json_end == -1 or json_end < json_start:
        return None
    candidate = payload[json_start : json_end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def _coerce_severity(value: str) -> Severity:
    try:
        return Severity(value.lower().strip())
    except ValueError:
        return Severity.LOW


def _extract_text(response: Any) -> str:
    if response is None:
        return ""
    if isinstance(response, str):
        return response
    for attr in ("completion", "content", "text", "output"):
        value = getattr(response, attr, None)
        if isinstance(value, str) and value:
            return value
    content = getattr(response, "content", None)
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
            else:
                parts.append(str(getattr(item, "text", "") or getattr(item, "content", "")))
        return "\n".join(p for p in parts if p)
    return str(response)


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
            response = await self._llm.ainvoke([UserMessage(content=prompt)])
            text = _extract_text(response)
            parsed = _parse_json_from_text(text)
            if parsed is None:
                return _degraded_judgement(
                    journey_name, browser_result, "Judge returned non-JSON output"
                )
            return _build_judgement(parsed)
        except Exception as exc:
            return _degraded_judgement(journey_name, browser_result, f"Judge call failed: {exc}")


def _build_judgement(parsed: dict[str, Any]) -> JourneyJudgement:
    findings_raw = parsed.get("findings") or parsed.get("issues") or []
    if isinstance(findings_raw, dict):
        findings_raw = [findings_raw]
    findings: list[FindingSchema] = []
    for raw in findings_raw:
        if not isinstance(raw, dict):
            continue
        findings.append(
            FindingSchema(
                severity=raw.get("severity") or raw.get("priority") or "low",
                title=raw.get("title") or raw.get("name") or "Untitled finding",
                page=raw.get("page") or raw.get("url") or raw.get("path") or "",
                viewport=raw.get("viewport") or "",
                expected=raw.get("expected") or raw.get("expected_behavior") or raw.get("expected_behavior") or "",
                actual=raw.get("actual") or raw.get("actual_behavior") or "",
                why_it_matters=raw.get("why_it_matters") or raw.get("impact") or raw.get("why") or "",
                reproduction_steps=raw.get("reproduction_steps") or raw.get("repro") or raw.get("steps") or [],
                evidence=raw.get("evidence") or raw.get("screenshots") or [],
                suggested_fix=raw.get("suggested_fix") or raw.get("fix") or raw.get("recommendation") or "",
            )
        )
    return JourneyJudgement(
        summary=parsed.get("summary") or "",
        status=parsed.get("status") or parsed.get("overall_status") or "passed",
        findings=findings,
        passed_checks=parsed.get("passed_checks") or parsed.get("passed") or [],
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
