
from pathlib import Path

import pytest

from app.services.repository_service import (
    UnsafeRepositoryPathError,
    list_repository_files,
    read_repository_file,
    resolve_workspace_path,
)


def test_rejects_parent_directory_traversal(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    with pytest.raises(UnsafeRepositoryPathError):
        resolve_workspace_path(workspace, "../outside.txt")


def test_rejects_absolute_path(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")

    with pytest.raises(UnsafeRepositoryPathError):
        read_repository_file(workspace, str(outside.resolve()))


def test_rejects_symlink_file(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")

    link = workspace / "linked.txt"

    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation is not permitted on this system.")

    with pytest.raises(UnsafeRepositoryPathError):
        read_repository_file(workspace, "linked.txt")


def test_file_listing_skips_symlinks(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    (workspace / "normal.py").write_text("print('ok')", encoding="utf-8")

    outside = tmp_path / "outside.py"
    outside.write_text("secret", encoding="utf-8")

    link = workspace / "linked.py"

    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation is not permitted on this system.")

    assert list_repository_files(workspace) == ["normal.py"]


def test_rejects_ignored_secret_files(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / ".env").write_text("API_KEY=secret", encoding="utf-8")

    with pytest.raises(UnsafeRepositoryPathError):
        read_repository_file(workspace, ".env")


def test_rejects_oversized_file(tmp_path: Path, monkeypatch):
    from app.config import get_settings

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "large.txt").write_text("x" * 100, encoding="utf-8")

    settings = get_settings()
    monkeypatch.setattr(settings, "max_read_file_size_kb", 0)

    with pytest.raises(ValueError, match="size limit must be positive"):
        read_repository_file(workspace, "large.txt")
