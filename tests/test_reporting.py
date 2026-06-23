from datetime import datetime, timezone

from tr_ai_card_radar.checks import run_checks
from tr_ai_card_radar.models import AuditResult, HfRepoSnapshot
from tr_ai_card_radar.reporting import build_report, render_markdown


def test_report_summary_counts() -> None:
    snapshot = HfRepoSnapshot(
        repo_id="local/mock-dataset",
        repo_type="dataset",
        tags=["language:tr"],
        card_data={"language": ["tr"]},
        card_text="# Mock",
    )
    result = AuditResult(snapshot=snapshot, warnings=run_checks(snapshot))
    report = build_report(result, checked_at=datetime(2026, 6, 23, tzinfo=timezone.utc))

    assert report["tool"] == "tr-ai-card-radar"
    assert report["checked_at"] == "2026-06-23T00:00:00Z"
    assert report["summary"]["blockers"] >= 1


def test_markdown_contains_boundary() -> None:
    snapshot = HfRepoSnapshot(
        repo_id="local/mock-model",
        repo_type="model",
        tags=["language:tr", "license:mit"],
        card_data={"language": ["tr"], "license": "mit", "base_model": "local/base"},
        card_text="# Mock\n\n## Intended Use\n\nTest only.\n\n## Limitations\n\nNo claim.",
    )
    result = AuditResult(snapshot=snapshot, warnings=run_checks(snapshot))
    report = build_report(result, checked_at=datetime(2026, 6, 23, tzinfo=timezone.utc))
    markdown = render_markdown(report)

    assert "does not provide legal advice" in markdown
    assert "clinical validation" in markdown
