"""Regression tests for packaging metadata URLs."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_urls_point_to_real_repository() -> None:
    text = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "REPLACE_WITH_USERNAME" not in text
    expected = "https://github.com/goktugozkanmd/tr-ai-card-radar"
    assert 'Homepage = "' + expected + '"' in text
    assert 'Issues = "' + expected + '/issues"' in text
