import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from tr_ai_card_radar.checks import run_checks
from tr_ai_card_radar.models import AuditResult, HfRepoSnapshot
from tr_ai_card_radar.reporting import build_report, render_markdown, write_report_bundle


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


def test_check_id_is_in_json_tsv_and_markdown(tmp_path: Path) -> None:
    snapshot = HfRepoSnapshot(repo_id="local/empty-dataset", repo_type="dataset", gated="manual")
    result = AuditResult(snapshot=snapshot, warnings=run_checks(snapshot))
    write_report_bundle(result, tmp_path)

    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    check_ids = [item["check_id"] for item in report["warnings"]]
    assert check_ids == [item.check_id for item in result.warnings]
    assert "LICENSE_MISSING" in check_ids

    with (tmp_path / "reuse_warnings.tsv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle, delimiter="\t"))
    assert rows[0] == ["repo_id", "repo_type", "severity", "check_id", "message"]
    assert [row[3] for row in rows[1:]] == check_ids

    markdown = (tmp_path / "report.md").read_text(encoding="utf-8")
    headings = [line for line in markdown.splitlines() if line.startswith("### ")]
    assert headings == [f"### {item['check_id']} ({item['severity']})" for item in report["warnings"]]
