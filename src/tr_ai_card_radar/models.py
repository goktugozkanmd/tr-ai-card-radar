from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

RepoType = Literal["model", "dataset"]
Severity = Literal["blocker", "warning", "info"]


@dataclass(frozen=True)
class HfRepoSnapshot:
    repo_id: str
    repo_type: RepoType
    source_url: str | None = None
    gated: bool | str | None = None
    private: bool | None = None
    tags: list[str] = field(default_factory=list)
    card_data: dict[str, Any] = field(default_factory=dict)
    card_text: str = ""
    sha: str | None = None
    siblings_count: int | None = None


@dataclass(frozen=True)
class WarningItem:
    check_id: str
    severity: Severity
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AuditResult:
    snapshot: HfRepoSnapshot
    warnings: list[WarningItem]
