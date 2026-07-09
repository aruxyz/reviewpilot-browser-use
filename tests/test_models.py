from reviewpilot.core.result import Finding, JourneyResult, ReviewReport
from reviewpilot.core.severity import ReviewStatus, Severity


def test_severity_ordering():
    ordered = Severity.order([Severity.LOW, Severity.CRITICAL, Severity.MEDIUM, Severity.HIGH])
    assert ordered == [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]


def test_severity_rank():
    assert Severity.CRITICAL.rank > Severity.HIGH.rank
    assert Severity.HIGH.rank > Severity.MEDIUM.rank
    assert Severity.MEDIUM.rank > Severity.LOW.rank


def test_finding_is_blocking():
    assert Finding(severity=Severity.CRITICAL, title="x").is_blocking is True
    assert Finding(severity=Severity.HIGH, title="x").is_blocking is True
    assert Finding(severity=Severity.MEDIUM, title="x").is_blocking is False
    assert Finding(severity=Severity.LOW, title="x").is_blocking is False


def test_report_recompute_status_passed():
    report = ReviewReport(app_name="A", app_url="http://x")
    report.recompute_status()
    assert report.status == ReviewStatus.PASSED


def test_report_recompute_status_failed_with_high_finding():
    report = ReviewReport(
        app_name="A",
        app_url="http://x",
        journeys=[
            JourneyResult(
                name="J",
                goal="G",
                status=ReviewStatus.FAILED,
                findings=[Finding(severity=Severity.HIGH, title="CTA hidden")],
            )
        ],
    )
    report.recompute_status()
    assert report.status == ReviewStatus.FAILED
    assert report.counts[Severity.HIGH] == 1


def test_report_recompute_status_errored():
    report = ReviewReport(
        app_name="A",
        app_url="http://x",
        journeys=[
            JourneyResult(name="J", goal="G", status=ReviewStatus.ERRORED, errors=["timeout"]),
        ],
    )
    report.recompute_status()
    assert report.status == ReviewStatus.ERRORED


def test_report_findings_by_severity():
    report = ReviewReport(
        app_name="A",
        app_url="http://x",
        journeys=[
            JourneyResult(
                name="J",
                goal="G",
                status=ReviewStatus.FAILED,
                findings=[
                    Finding(severity=Severity.HIGH, title="A"),
                    Finding(severity=Severity.LOW, title="B"),
                    Finding(severity=Severity.HIGH, title="C"),
                ],
            )
        ],
    )
    by_sev = report.findings_by_severity
    assert len(by_sev[Severity.HIGH]) == 2
    assert len(by_sev[Severity.LOW]) == 1
    assert len(by_sev[Severity.CRITICAL]) == 0
