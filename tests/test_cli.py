from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

from tr_ai_card_radar import cli
from tr_ai_card_radar.checks import run_checks
from tr_ai_card_radar.hf_client import FetchError
from tr_ai_card_radar.models import HfRepoSnapshot

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _mock_snapshot(repo_id: str, repo_type: str, source_url: str | None = None) -> HfRepoSnapshot:
    resolved_type = "model" if repo_type == "auto" else repo_type
    return HfRepoSnapshot(
        repo_id=repo_id,
        repo_type=resolved_type,  # type: ignore[arg-type]
        source_url=source_url,
        gated=False,
        private=False,
        tags=["language:tr", "license:mit"],
        card_data={"language": ["tr"], "license": "mit", "base_model": "org/base"},
        card_text="# Card\n\n## Intended Use\n\nTesting.\n\n## Limitations\n\nNone.\n\n## Dataset Sources\n\nLocal.\n",
        siblings_count=1,
    )


def test_cli_audit_writes_report_bundle(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        cli,
        "fetch_repo_snapshot",
        lambda repo_id, repo_type, source_url=None: _mock_snapshot(repo_id, repo_type, source_url),
    )
    out_dir = tmp_path / "single-report"

    cli.main(["audit", "org/turkish-model", "--repo-type", "model", "--out-dir", str(out_dir)])

    report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
    assert report["repo"]["repo_id"] == "org/turkish-model"
    assert report["summary"]["blockers"] == 0
    assert (out_dir / "report.md").is_file()
    assert (out_dir / "reuse_warnings.tsv").is_file()


def test_cli_audit_exits_cleanly_on_fetch_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def _boom(**_kwargs: object) -> HfRepoSnapshot:
        raise FetchError("Could not fetch Hugging Face repo snapshot for org/missing")

    monkeypatch.setattr(cli, "fetch_repo_snapshot", _boom)

    with pytest.raises(SystemExit, match="Error: Could not fetch Hugging Face repo snapshot"):
        cli.main(["audit", "org/missing", "--out-dir", str(tmp_path / "out")])


def test_cli_audit_list_writes_per_repo_directories(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        cli,
        "fetch_repo_snapshot",
        lambda repo_id, repo_type, source_url=None: _mock_snapshot(repo_id, repo_type, source_url),
    )
    yaml_path = tmp_path / "resources.yaml"
    yaml_path.write_text(
        yaml.safe_dump(
            {
                "resources": [
                    {"repo_id": "org/model-a", "repo_type": "model"},
                    {"repo_id": "org/dataset-b", "repo_type": "dataset"},
                ]
            }
        ),
        encoding="utf-8",
    )
    out_dir = tmp_path / "batch"

    cli.main(["audit-list", str(yaml_path), "--out-dir", str(out_dir)])

    assert (out_dir / "org__model-a" / "report.json").is_file()
    assert (out_dir / "org__dataset-b" / "report.json").is_file()


@pytest.mark.parametrize(
    ("content", "expected_msg"),
    [
        ("", "Error: no resources found"),
        ("- just-a-list\n", "Error: no resources found"),
        ("resources: []\n", "Error: no resources found"),
        ("resources:\n  - bad_entry\n", "must be a mapping"),
        ("resources:\n  - repo_type: model\n", "missing repo_id"),
        ("resources:\n  - repo_id: org/x\n    repo_type: space\n", "invalid repo_type"),
        ("resources: [unclosed\n", "Error: invalid YAML"),
    ],
)
def test_cli_audit_list_rejects_bad_yaml_with_clear_error(
    tmp_path: Path, content: str, expected_msg: str
) -> None:
    yaml_path = tmp_path / "bad.yaml"
    yaml_path.write_text(content, encoding="utf-8")

    with pytest.raises(SystemExit, match=expected_msg):
        cli.main(["audit-list", str(yaml_path), "--out-dir", str(tmp_path / "out")])


def test_cli_audit_list_missing_file_exits_cleanly(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.yaml"

    with pytest.raises(SystemExit, match="Error: resource file not found"):
        cli.main(["audit-list", str(missing), "--out-dir", str(tmp_path / "out")])


def test_shipped_examples_resources_yaml_matches_contract() -> None:
    payload = yaml.safe_load((PROJECT_ROOT / "examples" / "resources.yaml").read_text(encoding="utf-8"))
    resources = payload["resources"]
    assert len(resources) >= 1
    for item in resources:
        assert re.match(r"^[^/]+/[^/]+$", item["repo_id"])
        assert item["repo_type"] in {"model", "dataset"}
        assert item["source_url"].startswith("https://")
        assert len(item["reason"]) >= 10


def test_shipped_local_example_cards_have_no_blockers() -> None:
    cards = [
        ("examples/local_cards/model_card_minimal.md", "model"),
        ("examples/local_cards/dataset_card_minimal.md", "dataset"),
    ]
    for rel_path, repo_type in cards:
        raw = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        parts = raw.split("---", 2)
        assert len(parts) == 3, rel_path
        card_data = yaml.safe_load(parts[1])
        body = parts[2]
        snapshot = HfRepoSnapshot(
            repo_id=f"local/{Path(rel_path).stem}",
            repo_type=repo_type,  # type: ignore[arg-type]
            card_data=card_data,
            card_text=body,
            siblings_count=1,
        )
        warnings = run_checks(snapshot)
        blockers = [w for w in warnings if w.severity == "blocker"]
        assert blockers == [], f"{rel_path} produced unexpected blockers: {blockers}"
