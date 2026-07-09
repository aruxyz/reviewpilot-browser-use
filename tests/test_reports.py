from reviewpilot.core.result import Finding, JourneyResult, ReviewReport
from reviewpilot.core.severity import ReviewStatus, Severity
from reviewpilot.reports.html import generate_html_report
from reviewpilot.reports.markdown import generate_markdown_report, REPORT_MARKER


def _sample_report() -> ReviewReport:
    return ReviewReport(
        app_name="Demo",
        app_url="https://preview.demo.com",
        status=ReviewStatus.FAILED,
        journeys=[
            JourneyResult(
                name="Homepage review",
                goal="Check homepage",
                viewport="mobile",
                status=ReviewStatus.FAILED,
                findings=[
                    Finding(
                        severity=Severity.HIGH,
                        title="Primary CTA hidden below fold on mobile",
                        page="/",
                        viewport="mobile",
                        expected="CTA visible on initial load",
                        actual="CTA requires scrolling",
                        why_it_matters="Users may miss the main action",
                        reproduction_steps=["Open / on mobile", "Observe hero section"],
                        evidence=["screenshots/home-mobile-01.png"],
                        suggested_fix="Reduce hero padding on mobile",
                    ),
                    Finding(
                        severity=Severity.LOW,
                        title="Minor spacing inconsistency",
                        page="/",
                        viewport="desktop",
                        suggested_fix="Align spacing",
                    ),
                ],
                steps=15,
                duration_seconds=42.5,
            ),
            JourneyResult(
                name="Login flow",
                goal="Check login",
                viewport="desktop",
                status=ReviewStatus.PASSED,
                steps=8,
                duration_seconds=20.1,
            ),
        ],
        total_duration_seconds=62.6,
    )


def test_markdown_report_contains_marker():
    report = _sample_report()
    md = generate_markdown_report(report)
    assert REPORT_MARKER in md


def test_markdown_report_contains_findings():
    report = _sample_report()
    md = generate_markdown_report(report)
    assert "Primary CTA hidden below fold on mobile" in md
    assert "High Priority" in md
    assert "screenshots/home-mobile-01.png" in md
    assert "ReviewPilot Browser QA Report" in md
    assert "powered by Browser Use" in md


def test_markdown_report_contains_passed_checks():
    report = _sample_report()
    md = generate_markdown_report(report)
    assert "Login flow" in md


def test_html_report_generates_valid_html():
    report = _sample_report()
    html = generate_html_report(report)
    assert "<!DOCTYPE html>" in html
    assert "ReviewPilot" in html
    assert "Primary CTA hidden below fold on mobile" in html
    assert "review.html.j2" not in html


def test_markdown_report_passed_when_no_findings():
    report = ReviewReport(
        app_name="A",
        app_url="http://x",
        status=ReviewStatus.PASSED,
        journeys=[JourneyResult(name="J", goal="G", status=ReviewStatus.PASSED, steps=5, duration_seconds=10.0)],
    )
    md = generate_markdown_report(report)
    assert "Status: Passed" in md
    assert "0 issues" in md
