from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from .checks import run_checks
from .hf_client import fetch_repo_snapshot
from .models import AuditResult
from .reporting import write_report_bundle


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="tr-card-radar",
        description="Audit Hugging Face model and dataset card metadata.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser("audit", help="Audit one Hugging Face repository.")
    audit_parser.add_argument("repo_id", help="Hugging Face repository id, for example owner/name.")
    audit_parser.add_argument(
        "--repo-type",
        choices=["auto", "model", "dataset"],
        default="auto",
        help="Repository type. Use explicit model or dataset for reproducible runs.",
    )
    audit_parser.add_argument("--source-url", default=None, help="Optional public source URL.")
    audit_parser.add_argument(
        "--out-dir",
        default="reports/current",
        help="Output directory for report.json, report.md, and reuse_warnings.tsv.",
    )

    list_parser = subparsers.add_parser("audit-list", help="Audit repositories from YAML.")
    list_parser.add_argument("resources_yaml", help="Path to examples/resources.yaml style file.")
    list_parser.add_argument(
        "--out-dir",
        default="reports",
        help="Output directory for per repository report folders.",
    )

    args = parser.parse_args(argv)

    if args.command == "audit":
        result = _audit_one(args.repo_id, args.repo_type, args.source_url)
        write_report_bundle(result, Path(args.out_dir))
        return

    if args.command == "audit-list":
        _audit_list(Path(args.resources_yaml), Path(args.out_dir))
        return

    parser.error("unknown command")


def _audit_one(repo_id: str, repo_type: str, source_url: str | None) -> AuditResult:
    snapshot = fetch_repo_snapshot(repo_id=repo_id, repo_type=repo_type, source_url=source_url)
    return AuditResult(snapshot=snapshot, warnings=run_checks(snapshot))


def _audit_list(resources_path: Path, out_dir: Path) -> None:
    payload = yaml.safe_load(resources_path.read_text(encoding="utf-8"))
    resources = payload.get("resources", [])
    if not resources:
        raise SystemExit(f"No resources found in {resources_path}")

    for item in resources:
        repo_id = item["repo_id"]
        repo_type = item["repo_type"]
        source_url = item.get("source_url")
        result = _audit_one(repo_id=repo_id, repo_type=repo_type, source_url=source_url)
        repo_dir = out_dir / _safe_repo_dir(repo_id)
        write_report_bundle(result, repo_dir)


def _safe_repo_dir(repo_id: str) -> str:
    return repo_id.replace("/", "__").replace(" ", "_")
