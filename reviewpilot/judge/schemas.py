from __future__ import annotations

from pydantic import BaseModel, Field


class FindingSchema(BaseModel):
    severity: str = Field(description="One of: critical, high, medium, low")
    title: str
    page: str = ""
    viewport: str = ""
    expected: str = ""
    actual: str = ""
    why_it_matters: str = ""
    reproduction_steps: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    suggested_fix: str = ""


class JourneyJudgement(BaseModel):
    summary: str = Field(description="One or two sentence overall summary of the journey outcome.")
    status: str = Field(description="One of: passed, failed, errored")
    findings: list[FindingSchema] = Field(default_factory=list)
    passed_checks: list[str] = Field(
        default_factory=list,
        description="Names of checks or sub-flows that passed without issues.",
    )
