from __future__ import annotations

import re
from typing import Any

from .models import HfRepoSnapshot, WarningItem

LICENSE_PATTERNS = [
    "apache-2.0",
    "apache 2.0",
    "mit",
    "afl-3.0",
    "cc-by-4.0",
    "cc by 4.0",
    "cc-by-nc-4.0",
    "cc by-nc 4.0",
    "cc-by-nc-nd-4.0",
    "cc by-nc-nd 4.0",
    "gemma",
]

SOURCE_KEYWORDS = [
    "dataset sources",
    "data sources",
    "source data",
    "data source",
    "dataset creation",
    "creation process",
    "collection process",
    "veri kaynagi",
    "veri kaynağı",
]

INTENDED_USE_KEYWORDS = ["intended use", "uses", "usage", "kullanim", "kullanım"]
LIMITATION_KEYWORDS = ["limitations", "limitation", "sinirlar", "sınırlamalar", "limits"]
TRAINING_DATA_KEYWORDS = ["training data", "datasets", "dataset", "egitim verisi", "eğitim verisi"]


def run_checks(snapshot: HfRepoSnapshot) -> list[WarningItem]:
    warnings: list[WarningItem] = []
    warnings.extend(_license_checks(snapshot))
    warnings.extend(_language_checks(snapshot))
    warnings.extend(_access_checks(snapshot))
    warnings.extend(_card_text_checks(snapshot))

    if snapshot.repo_type == "model":
        warnings.extend(_model_checks(snapshot))
    elif snapshot.repo_type == "dataset":
        warnings.extend(_dataset_checks(snapshot))

    warnings.append(
        WarningItem(
            check_id="not_legal_advice",
            severity="info",
            message="This report is a metadata warning aid and does not provide legal advice.",
        )
    )
    return warnings


def _license_checks(snapshot: HfRepoSnapshot) -> list[WarningItem]:
    warnings: list[WarningItem] = []
    metadata_licenses = _metadata_licenses(snapshot)
    prose_mentions = _prose_license_mentions(snapshot.card_text)

    if not metadata_licenses and not prose_mentions:
        warnings.append(
            WarningItem(
                check_id="missing_license",
                severity="blocker",
                message="No license was found in Hub metadata, card metadata, or simple card prose scan.",
                evidence={
                    "metadata_license": metadata_licenses,
                    "prose_license_mentions": sorted(prose_mentions),
                },
            )
        )
        return warnings

    if metadata_licenses and prose_mentions:
        normalized_metadata = {_normalize_license(item) for item in metadata_licenses}
        normalized_prose = {_normalize_license(item) for item in prose_mentions}
        if normalized_metadata.isdisjoint(normalized_prose):
            warnings.append(
                WarningItem(
                    check_id="license_metadata_prose_mismatch",
                    severity="warning",
                    message=(
                        "License string in metadata does not match simple license mentions "
                        "found in card prose. Human review is needed."
                    ),
                    evidence={
                        "metadata_license": sorted(metadata_licenses),
                        "prose_license_mentions": sorted(prose_mentions),
                    },
                )
            )

    return warnings


def _language_checks(snapshot: HfRepoSnapshot) -> list[WarningItem]:
    languages = _as_list(snapshot.card_data.get("language"))
    tag_languages = [tag for tag in snapshot.tags if tag.startswith("language:")]
    turkish_tags = [tag for tag in snapshot.tags if "turkish" in tag.lower()]

    if not languages and not tag_languages and not turkish_tags:
        return [
            WarningItem(
                check_id="missing_language",
                severity="warning",
                message="No language metadata was found in card data or repository tags.",
                evidence={"card_language": languages, "language_tags": tag_languages},
            )
        ]
    return []


def _access_checks(snapshot: HfRepoSnapshot) -> list[WarningItem]:
    if snapshot.gated in (True, "auto", "manual"):
        return [
            WarningItem(
                check_id="gated_access_review_needed",
                severity="warning",
                message=(
                    "Repository appears to be gated. The tool must not download protected rows "
                    "or treat access as reuse permission."
                ),
                evidence={"gated": snapshot.gated},
            )
        ]
    return []


def _card_text_checks(snapshot: HfRepoSnapshot) -> list[WarningItem]:
    if snapshot.card_text.strip():
        return []
    return [
        WarningItem(
            check_id="missing_card_text",
            severity="warning",
            message="No README card text was available for prose checks.",
            evidence={},
        )
    ]


def _model_checks(snapshot: HfRepoSnapshot) -> list[WarningItem]:
    warnings: list[WarningItem] = []
    card = snapshot.card_data
    text = _lower_ascii(snapshot.card_text)

    base_model = card.get("base_model") or card.get("base_models")
    tag_base_model = [tag for tag in snapshot.tags if tag.startswith("base_model:")]
    if not base_model and not tag_base_model:
        warnings.append(
            WarningItem(
                check_id="missing_base_model",
                severity="warning",
                message="No base model metadata was found.",
                evidence={"base_model": base_model, "base_model_tags": tag_base_model},
            )
        )

    if not _contains_any(text, INTENDED_USE_KEYWORDS):
        warnings.append(
            WarningItem(
                check_id="missing_intended_use",
                severity="warning",
                message="Model card text does not clearly mention intended use.",
                evidence={"keywords_checked": INTENDED_USE_KEYWORDS},
            )
        )

    if not _contains_any(text, LIMITATION_KEYWORDS):
        warnings.append(
            WarningItem(
                check_id="missing_limitations",
                severity="warning",
                message="Model card text does not clearly mention limitations.",
                evidence={"keywords_checked": LIMITATION_KEYWORDS},
            )
        )

    if not card.get("datasets") and not _contains_any(text, TRAINING_DATA_KEYWORDS):
        warnings.append(
            WarningItem(
                check_id="missing_training_data_surface",
                severity="info",
                message="Model card does not clearly surface datasets or training data notes.",
                evidence={"card_datasets": card.get("datasets")},
            )
        )

    return warnings


def _dataset_checks(snapshot: HfRepoSnapshot) -> list[WarningItem]:
    warnings: list[WarningItem] = []
    text = _lower_ascii(snapshot.card_text)

    if not _contains_any(text, SOURCE_KEYWORDS):
        warnings.append(
            WarningItem(
                check_id="missing_dataset_source_statement",
                severity="warning",
                message="Dataset card text does not clearly mention source data or creation process.",
                evidence={"keywords_checked": SOURCE_KEYWORDS},
            )
        )

    data_files = snapshot.card_data.get("data_files")
    configs = snapshot.card_data.get("configs")
    if data_files is None and configs is None and snapshot.siblings_count in (None, 0):
        warnings.append(
            WarningItem(
                check_id="missing_visible_data_file_surface",
                severity="info",
                message="No visible data file metadata was found in public card data snapshot.",
                evidence={
                    "data_files": data_files,
                    "configs": configs,
                    "siblings_count": snapshot.siblings_count,
                },
            )
        )

    return warnings


def _metadata_licenses(snapshot: HfRepoSnapshot) -> set[str]:
    values = set(_as_list(snapshot.card_data.get("license")))
    values.update(_as_list(snapshot.card_data.get("licenses")))
    for tag in snapshot.tags:
        if tag.startswith("license:"):
            values.add(tag.split(":", 1)[1])
    return {str(value).strip().lower() for value in values if str(value).strip()}


def _prose_license_mentions(text: str) -> set[str]:
    low = _lower_ascii(text)
    found: set[str] = set()
    for pattern in LICENSE_PATTERNS:
        if pattern in low:
            found.add(pattern)
    return found


def _normalize_license(value: str) -> str:
    value = value.lower().strip()
    value = value.replace(" ", "-")
    value = re.sub(r"-+", "-", value)
    return value


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(_lower_ascii(keyword) in text for keyword in keywords)


def _lower_ascii(text: str) -> str:
    return text.casefold()
