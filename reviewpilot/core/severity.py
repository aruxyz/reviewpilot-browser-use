from enum import Enum


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def rank(self) -> int:
        return _RANK[self]

    @property
    def emoji(self) -> str:
        return _EMOJI[self]

    @classmethod
    def order(cls, severities: list["Severity"]) -> list["Severity"]:
        return sorted(severities, key=lambda s: s.rank, reverse=True)


_RANK = {
    Severity.CRITICAL: 4,
    Severity.HIGH: 3,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
}

_EMOJI = {
    Severity.CRITICAL: "🔴",
    Severity.HIGH: "🟠",
    Severity.MEDIUM: "🟡",
    Severity.LOW: "🔵",
}


class ReviewStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    ERRORED = "errored"
    SKIPPED = "skipped"
