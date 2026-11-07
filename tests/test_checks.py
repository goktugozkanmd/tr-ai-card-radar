from tr_ai_card_radar.checks import run_checks
from tr_ai_card_radar.models import HfRepoSnapshot

# The ten v0.1 check ids, matching the "What it checks" list in README.md.
EXPECTED_CHECK_IDS = {
    "LICENSE_MISSING",
    "LICENSE_PROSE_MISMATCH",
    "LANGUAGE_MISSING",
    "ACCESS_GATED",
    "MODEL_BASE_MODEL_MISSING",
    "MODEL_INTENDED_USE_MISSING",
    "MODEL_LIMITATIONS_MISSING",
    "DATASET_SOURCE_MISSING",
    "DATASET_SPLIT_NOTES_MISSING",
    "CARD_TEXT_MISSING",
}

# Warnings with no v0.1 id. They keep their existing lowercase ids.
UNLISTED_CHECK_IDS = {"missing_training_data_surface", "not_legal_advice"}


def _sample_snapshots() -> list[HfRepoSnapshot]:
    return [
        HfRepoSnapshot(repo_id="local/empty-dataset", repo_type="dataset", gated="manual"),
        HfRepoSnapshot(
            repo_id="local/mismatch-model",
            repo_type="model",
            tags=["language:tr", "license:cc-by-nc-nd-4.0"],
            card_data={"language": ["tr"], "license": "cc-by-nc-nd-4.0"},
            card_text="# Mock\n\nLicense: CC BY-NC 4.0\n\nTest only.",
        ),
        HfRepoSnapshot(
            repo_id="local/bare-model",
            repo_type="model",
            tags=["language:tr", "license:mit"],
            card_data={"language": ["tr"], "license": "mit"},
            card_text="# Mock",
        ),
    ]


def test_dataset_missing_license_is_blocker() -> None:
    snapshot = HfRepoSnapshot(
        repo_id="local/mock-dataset",
        repo_type="dataset",
        tags=["language:tr"],
        card_data={"language": ["tr"]},
        card_text="# Mock\n\nNo source statement here.",
    )

    warnings = run_checks(snapshot)

    assert any(item.check_id == "LICENSE_MISSING" and item.severity == "blocker" for item in warnings)


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

    assert not any(item.check_id == "DATASET_SOURCE_MISSING" for item in warnings)


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

    assert any(item.check_id == "LICENSE_PROSE_MISMATCH" for item in warnings)


def test_model_missing_base_model_is_warning() -> None:
    snapshot = HfRepoSnapshot(
        repo_id="local/mock-model",
        repo_type="model",
        tags=["language:tr", "license:mit"],
        card_data={"language": ["tr"], "license": "mit"},
        card_text="# Mock\n\n## Intended Use\n\nTest only.\n\n## Limitations\n\nNo quality claim.",
    )

    warnings = run_checks(snapshot)

    assert any(
        item.check_id == "MODEL_BASE_MODEL_MISSING" and item.severity == "warning" for item in warnings
    )


def test_licenseless_card_with_incidental_mit_word_is_still_blocker() -> None:
    snapshot = HfRepoSnapshot(
        repo_id="local/mock-model",
        repo_type="model",
        tags=["language:tr"],
        card_data={"language": ["tr"]},
        card_text=(
            "# Mock\n\n## Intended Use\n\nResearch only; do not submit outputs for diagnosis.\n"
            "A permit is required for any clinical use.\n\n## Limitations\n\nNot validated."
        ),
    )

    warnings = run_checks(snapshot)

    assert any(item.check_id == "LICENSE_MISSING" and item.severity == "blocker" for item in warnings)


def test_every_emitted_warning_has_a_known_check_id() -> None:
    for snapshot in _sample_snapshots():
        for item in run_checks(snapshot):
            assert item.check_id in EXPECTED_CHECK_IDS | UNLISTED_CHECK_IDS, item.check_id


def test_every_v01_check_id_can_be_emitted() -> None:
    emitted = {item.check_id for snapshot in _sample_snapshots() for item in run_checks(snapshot)}

    assert EXPECTED_CHECK_IDS <= emitted
