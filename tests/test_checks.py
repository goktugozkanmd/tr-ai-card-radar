from tr_ai_card_radar.checks import run_checks
from tr_ai_card_radar.models import HfRepoSnapshot


def test_dataset_missing_license_is_blocker() -> None:
    snapshot = HfRepoSnapshot(
        repo_id="local/mock-dataset",
        repo_type="dataset",
        tags=["language:tr"],
        card_data={"language": ["tr"]},
        card_text="# Mock\n\nNo source statement here.",
    )

    warnings = run_checks(snapshot)

    assert any(item.check_id == "missing_license" and item.severity == "blocker" for item in warnings)


def test_dataset_source_statement_passes_when_present() -> None:
    snapshot = HfRepoSnapshot(
        repo_id="local/mock-dataset",
        repo_type="dataset",
        tags=["language:tr", "license:mit"],
        card_data={"language": ["tr"], "license": "mit"},
        card_text="# Mock\n\n## Dataset Sources\n\nSelf written examples.",
        siblings_count=1,
    )

    warnings = run_checks(snapshot)

    assert not any(item.check_id == "missing_dataset_source_statement" for item in warnings)


def test_license_metadata_prose_mismatch_is_warning() -> None:
    snapshot = HfRepoSnapshot(
        repo_id="local/mock-dataset",
        repo_type="dataset",
        tags=[],
        card_data={"license": "cc-by-nc-nd-4.0", "language": ["tr"]},
        card_text="# Mock\n\nLicense: CC BY-NC 4.0\n\n## Dataset Sources\n\nSelf written.",
        siblings_count=1,
    )

    warnings = run_checks(snapshot)

    assert any(item.check_id == "license_metadata_prose_mismatch" for item in warnings)


def test_model_missing_base_model_is_warning() -> None:
    snapshot = HfRepoSnapshot(
        repo_id="local/mock-model",
        repo_type="model",
        tags=["language:tr", "license:mit"],
        card_data={"language": ["tr"], "license": "mit"},
        card_text="# Mock\n\n## Intended Use\n\nTest only.\n\n## Limitations\n\nNo quality claim.",
    )

    warnings = run_checks(snapshot)

    assert any(item.check_id == "missing_base_model" and item.severity == "warning" for item in warnings)
