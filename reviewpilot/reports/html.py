from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from reviewpilot.core.result import ReviewReport

_TEMPLATE_DIR = Path(__file__).parent / "templates"


def _make_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )


def generate_html_report(report: ReviewReport) -> str:
    env = _make_env()
    template = env.get_template("review.html.j2")
    return template.render(
        report=report,
        counts=report.counts,
        findings_by_severity=report.findings_by_severity,
        any_findings=bool(report.all_findings),
        passed_checks=report.passed_checks,
    )


def write_html_report(report: ReviewReport, output_path: Path) -> Path:
    html = generate_html_report(report)
    output_path.write_text(html, encoding="utf-8")
    return output_path
