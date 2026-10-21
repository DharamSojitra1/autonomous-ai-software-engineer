from pathlib import Path

import pytest

from app.services.repository_service import (
    UnsafeRepositoryPathError,
    list_repository_files,
    resolve_workspace_path,
)


def test_list_repository_files_excludes_ignored_files(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / ".env").write_text("SECRET=value", encoding="utf-8")

    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("internal", encoding="utf-8")

    files = list_repository_files(tmp_path)

    assert files == ["src/main.py"]


def test_resolve_workspace_path_accepts_internal_path(tmp_path: Path):
    (tmp_path / "src").mkdir()

    result = resolve_workspace_path(tmp_path, "src")

    assert result == (tmp_path / "src").resolve()


def test_resolve_workspace_path_rejects_parent_traversal(tmp_path: Path):
    with pytest.raises(UnsafeRepositoryPathError):
        resolve_workspace_path(tmp_path, "../outside.txt")
