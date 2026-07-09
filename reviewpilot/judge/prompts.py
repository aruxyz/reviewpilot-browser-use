from __future__ import annotations

from typing import Any

SEVERITY_RUBRIC = """\
Severity rubric (use these exact values):
- critical: The user cannot complete an important flow. Examples: login impossible, checkout cannot proceed, main page crashes, navigation completely broken.
- high: The user can continue but the issue seriously damages usability. Examples: primary CTA hidden, form validation unclear, mobile layout blocks important actions, key button does nothing.
- medium: Noticeable but not blocking. Examples: minor layout overflow, inconsistent spacing, missing empty state, weak visual hierarchy.
- low: Small polish issues. Examples: minor copy issue, slight alignment problem, non-critical console warning.
"""


def build_judge_prompt(journey_name: str, journey_goal: str, viewport: str, browser_result: dict[str, Any]) -> str:
    final_result = browser_result.get("final_result") or "(no final result returned)"
    errors = browser_result.get("errors") or []
    urls = browser_result.get("urls") or []
    actions = browser_result.get("actions") or []
    screenshots = browser_result.get("screenshot_paths") or []
    steps = browser_result.get("steps") or 0
    is_successful = browser_result.get("is_successful")

    errors_block = "\n".join(f"- {e}" for e in errors) if errors else "(none)"
    urls_block = "\n".join(f"- {u}" for u in urls[:20]) if urls else "(none)"
    actions_block = "\n".join(f"- {a}" for a in actions[:30]) if actions else "(none)"
    screenshots_block = "\n".join(f"- {s}" for s in screenshots[:10]) if screenshots else "(none)"

    success_hint = "successful" if is_successful else "not marked successful"

    return (
        f"You are judging a Browser Use agent run to produce a structured QA report.\n\n"
        f"Journey: {journey_name}\n"
        f"Goal: {journey_goal}\n"
        f"Viewport: {viewport}\n"
        f"Steps taken: {steps}\n"
        f"Run status: {success_hint}\n\n"
        f"Agent final result:\n{final_result}\n\n"
        f"Errors observed:\n{errors_block}\n\n"
        f"URLs visited:\n{urls_block}\n\n"
        f"Actions taken:\n{actions_block}\n\n"
        f"Screenshots captured (relative paths):\n{screenshots_block}\n\n"
        f"{SEVERITY_RUBRIC}\n"
        f"Instructions:\n"
        f"- Produce a concise summary of the journey outcome.\n"
        f"- Set status to 'passed' if no critical/high issues, 'failed' if any high/critical findings, 'errored' if the run itself broke.\n"
        f"- List every user-facing issue as a finding with severity, expected vs actual behavior, why it matters, reproduction steps, and a suggested fix.\n"
        f"- Reference screenshot paths in the evidence field when relevant.\n"
        f"- If the agent did not actually observe a real issue, do not invent one. Only report issues backed by the run evidence.\n"
        f"- List passed_checks for sub-flows that worked correctly.\n\n"
        f"Respond with ONLY a single JSON object. No prose, no code, no markdown fences.\n"
        f"The JSON MUST use this exact schema:\n"
        f"{{\n"
        f'  "summary": "one or two sentence summary",\n'
        f'  "status": "passed | failed | errored",\n'
        f'  "findings": [\n'
        f"    {{\n"
        f'      "severity": "critical | high | medium | low",\n'
        f'      "title": "short title",\n'
        f'      "page": "/path",\n'
        f'      "viewport": "desktop | mobile",\n'
        f'      "expected": "what should happen",\n'
        f'      "actual": "what actually happened",\n'
        f'      "why_it_matters": "user impact",\n'
        f'      "reproduction_steps": ["step 1", "step 2"],\n'
        f'      "evidence": ["screenshots/x.png"],\n'
        f'      "suggested_fix": "how to fix"\n'
        f"    }}\n"
        f"  ],\n"
        f'  "passed_checks": ["check that worked"]\n'
        f"}}\n"
        f"Start your response with {{ and end with }}. Do not include any other text.\n"
    )
