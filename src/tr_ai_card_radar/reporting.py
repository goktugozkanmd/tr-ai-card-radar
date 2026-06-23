from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .models import AuditResult, WarningItem


def build_report(result: AuditResult, checked_at: datetime | None = None) -> dict[str, Any]:
    checked_at = checked_at or datetime.now(timezone.utc)
    warnings = [asdict(item) for item in result.warnings]
    return {
        "tool": "tr-ai-card-radar",
        "tool_version": __version__,
        "checked_at": checked_at.isoformat().replace("+00:00", "Z"),
        "repo": _snapshot_public_dict(result),
        "summary": {
            "blockers": _count(result.warnings, "blocker"),
            "warnings": _count(result.warnings, "warning"),
            "infos": _count(result.warnings, "info"),
        },
        "warnings": warnings,
    }


def write_report_bundle(result: AuditResult, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    report = build_report(result)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "report.md").write_text(render_markdown(report), encoding="utf-8")
    write_reuse_warnings_tsv(report, out_dir / "reuse_warnings.tsv")


def render_markdown(report: dict[str, Any]) -> str:
    repo = report["repo"]
    rows = [
        "# tr-ai-card-radar report",
        "",
        f"Repository: `{repo['repo_id']}`",
        "",
        f"Type: `{repo['repo_type']}`",
        "",
        f"Checked at: `{report['checked_at']}`",
        "",
        "## Summary",
        "",
        f"- Blockers: {report['summary']['blockers']}",
        f"- Warnings: {report['summary']['warnings']}",
        f"- Info: {report['summary']['infos']}",
        "",
        "## Warnings",
        "",
        "| Severity | Check | Message |",
        "|---|---|---|",
    ]
    for item in report["warnings"]:
        rows.append(
            f"| {item['severity']} | {item['check_id']} | "
            f"{_escape_table(item['message'])} |"
        )
    rows.extend(
        [
            "",
            "## Boundary",
            "",
            "This report does not provide legal advice, clinical validation, model ranking, "
            "or reuse permission.",
            "",
        ]
    )
    return "\n".join(rows)


def write_reuse_warnings_tsv(report: dict[str, Any], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["repo_id", "repo_type", "severity", "check_id", "message"],
            delimiter="\t",
        )
        writer.writeheader()
        for item in report["warnings"]:
            writer.writerow(
                {
                    "repo_id": report["repo"]["repo_id"],
                    "repo_type": report["repo"]["repo_type"],
                    "severity": item["severity"],
                    "check_id": item["check_id"],
                    "message": item["message"],
                }
            )


def _snapshot_public_dict(result: AuditResult) -> dict[str, Any]:
    snapshot = result.snapshot
    return {
        "repo_id": snapshot.repo_id,
        "repo_type": snapshot.repo_type,
        "source_url": snapshot.source_url,
        "gated": snapshot.gated,
        "private": snapshot.private,
        "sha": snapshot.sha,
        "tags": snapshot.tags,
        "card_data": snapshot.card_data,
        "siblings_count": snapshot.siblings_count,
    }


def _count(warnings: list[WarningItem], severity: str) -> int:
    return sum(1 for item in warnings if item.severity == severity)


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
