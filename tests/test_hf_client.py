from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from huggingface_hub.errors import RepositoryNotFoundError

from tr_ai_card_radar import hf_client


class _FakeCardData:
    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)


def test_repo_type_candidates_and_validation() -> None:
    assert hf_client._repo_type_candidates("model") == ["model"]
    assert hf_client._repo_type_candidates("dataset") == ["dataset"]
    assert hf_client._repo_type_candidates("auto") == ["model", "dataset"]
    with pytest.raises(ValueError, match="repo_type must be one of"):
        hf_client._repo_type_candidates("space")


def test_card_data_to_dict_variants() -> None:
    assert hf_client._card_data_to_dict(None) == {}
    assert hf_client._card_data_to_dict({"license": "mit"}) == {"license": "mit"}
    assert hf_client._card_data_to_dict(_FakeCardData({"language": ["tr"]})) == {"language": ["tr"]}
    assert hf_client._card_data_to_dict(object()) == {}


def test_download_readme_omits_deprecated_symlinks_arg(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured_kwargs: dict[str, Any] = {}

    def _fake_download(**kwargs: Any) -> str:
        captured_kwargs.update(kwargs)
        out = Path(kwargs["local_dir"]) / "README.md"
        out.write_text("# Sample Card\n", encoding="utf-8")
        return str(out)

    monkeypatch.setattr(hf_client, "hf_hub_download", _fake_download)

    text = hf_client._download_readme("org/model", "model", token=None)

    assert text == "# Sample Card\n"
    assert "local_dir_use_symlinks" not in captured_kwargs
    assert captured_kwargs["repo_id"] == "org/model"
    assert captured_kwargs["filename"] == "README.md"
    assert captured_kwargs["repo_type"] is None


def test_fetch_repo_snapshot_auto_falls_back_to_dataset(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str | None] = []

    class _FakeHfApi:
        def __init__(self, token: str | None = None) -> None:
            self.token = token

        def repo_info(self, repo_id: str, repo_type: str | None = None) -> Any:
            calls.append(repo_type)
            if repo_type is None:
                raise RepositoryNotFoundError("not a model")
            return SimpleNamespace(
                gated=False,
                private=False,
                tags=["language:tr", "license:mit"],
                cardData=_FakeCardData({"language": ["tr"], "license": "mit"}),
                sha="abc123",
                siblings=[object(), object()],
            )

    monkeypatch.setattr(hf_client, "HfApi", _FakeHfApi)
    monkeypatch.setattr(hf_client, "_download_readme", lambda *_args, **_kwargs: "# Dataset")

    snapshot = hf_client.fetch_repo_snapshot("org/turkish-ds", repo_type="auto")

    assert calls == [None, "dataset"]
    assert snapshot.repo_type == "dataset"
    assert snapshot.sha == "abc123"
    assert snapshot.siblings_count == 2
    assert snapshot.card_data == {"language": ["tr"], "license": "mit"}
    assert snapshot.card_text == "# Dataset"


def test_fetch_repo_snapshot_raises_fetch_error_when_all_candidates_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FailingHfApi:
        def __init__(self, token: str | None = None) -> None:
            self.token = token

        def repo_info(self, repo_id: str, repo_type: str | None = None) -> Any:
            raise RepositoryNotFoundError(f"missing {repo_id}")

    monkeypatch.setattr(hf_client, "HfApi", _FailingHfApi)

    with pytest.raises(hf_client.FetchError, match="Could not fetch Hugging Face repo snapshot"):
        hf_client.fetch_repo_snapshot("org/missing", repo_type="auto")
