from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.errors import GatedRepoError, HfHubHTTPError, RepositoryNotFoundError

from .models import HfRepoSnapshot, RepoType


class FetchError(RuntimeError):
    """Raised when a repository snapshot cannot be fetched."""


def fetch_repo_snapshot(
    repo_id: str,
    repo_type: str = "auto",
    token: str | None = None,
    source_url: str | None = None,
) -> HfRepoSnapshot:
    token = token or os.getenv("HF_TOKEN")
    errors: list[str] = []
    candidates = _repo_type_candidates(repo_type)

    for candidate in candidates:
        try:
            return _fetch_with_type(repo_id, candidate, token=token, source_url=source_url)
        except (RepositoryNotFoundError, GatedRepoError, HfHubHTTPError) as exc:
            errors.append(f"{candidate}: {exc}")

    joined = "; ".join(errors) if errors else "no candidate repo type tried"
    raise FetchError(f"Could not fetch Hugging Face repo snapshot for {repo_id}: {joined}")


def _fetch_with_type(
    repo_id: str,
    repo_type: RepoType,
    token: str | None,
    source_url: str | None,
) -> HfRepoSnapshot:
    api = HfApi(token=token)
    hub_repo_type = _hub_repo_type(repo_type)
    info = api.repo_info(repo_id=repo_id, repo_type=hub_repo_type)

    card_text = _download_readme(repo_id, repo_type, token)
    tags = [str(tag) for tag in getattr(info, "tags", []) or []]
    card_data = _card_data_to_dict(getattr(info, "cardData", None))
    siblings = getattr(info, "siblings", None) or []

    return HfRepoSnapshot(
        repo_id=repo_id,
        repo_type=repo_type,
        source_url=source_url,
        gated=getattr(info, "gated", None),
        private=getattr(info, "private", None),
        tags=tags,
        card_data=card_data,
        card_text=card_text,
        sha=getattr(info, "sha", None),
        siblings_count=len(siblings),
    )


def _download_readme(repo_id: str, repo_type: RepoType, token: str | None) -> str:
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = hf_hub_download(
                repo_id=repo_id,
                filename="README.md",
                repo_type=_hub_repo_type(repo_type),
                token=token,
                local_dir=tmpdir,
                local_dir_use_symlinks=False,
            )
            return Path(path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _repo_type_candidates(repo_type: str) -> list[RepoType]:
    if repo_type == "model":
        return ["model"]
    if repo_type == "dataset":
        return ["dataset"]
    if repo_type == "auto":
        return ["model", "dataset"]
    raise ValueError("repo_type must be one of: auto, model, dataset")


def _hub_repo_type(repo_type: RepoType) -> str | None:
    return None if repo_type == "model" else repo_type


def _card_data_to_dict(card_data: Any) -> dict[str, Any]:
    if card_data is None:
        return {}
    if isinstance(card_data, dict):
        return dict(card_data)
    if hasattr(card_data, "to_dict"):
        return dict(card_data.to_dict())
    try:
        return dict(card_data)
    except Exception:
        return {}
