from pathlib import Path

import pytest

from app.config import get_settings
from app.services.repository_service import search_repository_code


def test_search_finds_matching_line(tmp_path: Path):
    (tmp_path / "main.py").write_text(
        "def calculate_total():\n    return 42\n",
        encoding="utf-8",
    )

    results = search_repository_code(tmp_path, "return 42")

    assert len(results) == 1
    assert results[0]["path"] == "main.py"
    assert results[0]["line"] == 2
    assert results[0]["text"] == "    return 42"


def test_search_is_case_insensitive_by_default(tmp_path: Path):
    (tmp_path / "main.py").write_text("TODO: fix this\n", encoding="utf-8")

    results = search_repository_code(tmp_path, "todo")

    assert len(results) == 1


def test_search_can_be_case_sensitive(tmp_path: Path):
    (tmp_path / "main.py").write_text("TODO: fix this\n", encoding="utf-8")

    results = search_repository_code(
        tmp_path,
        "todo",
        case_sensitive=True,
    )

    assert results == []


def test_search_skips_env_files(tmp_path: Path):
    (tmp_path / ".env").write_text("API_KEY=secret\n", encoding="utf-8")
    (tmp_path / "main.py").write_text("API_KEY = config\n", encoding="utf-8")

    results = search_repository_code(tmp_path, "API_KEY")

    assert len(results) == 1
    assert results[0]["path"] == "main.py"


def test_search_rejects_empty_query(tmp_path: Path):
    with pytest.raises(ValueError, match="cannot be empty"):
        search_repository_code(tmp_path, "   ")


def test_search_respects_result_limit(tmp_path: Path, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "max_search_results", 2)

    (tmp_path / "main.py").write_text(
        "MATCH\nMATCH\nMATCH\n",
        encoding="utf-8",
    )

    results = search_repository_code(tmp_path, "MATCH")

    assert len(results) == 2
