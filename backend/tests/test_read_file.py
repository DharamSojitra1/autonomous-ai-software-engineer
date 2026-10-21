from pathlib import Path

import pytest

from app.services.repository_service import (
    UnsafeRepositoryPathError,
    read_repository_file,
)


def test_read_repository_file_returns_text(tmp_path: Path):
    source = tmp_path / "main.py"
    source.write_text("print('hello')\n", encoding="utf-8")

    result = read_repository_file(tmp_path, "main.py")

    assert result == "print('hello')\n"


def test_read_repository_file_rejects_parent_traversal(tmp_path: Path):
    with pytest.raises(UnsafeRepositoryPathError):
        read_repository_file(tmp_path, "../outside.txt")


def test_read_repository_file_rejects_env_file(tmp_path: Path):
    (tmp_path / ".env").write_text("API_KEY=secret", encoding="utf-8")

    with pytest.raises(UnsafeRepositoryPathError):
        read_repository_file(tmp_path, ".env")


def test_read_repository_file_rejects_binary_content(tmp_path: Path):
    (tmp_path / "binary.dat").write_bytes(b"\xff\xfe\x00")

    with pytest.raises(ValueError, match="UTF-8"):
        read_repository_file(tmp_path, "binary.dat")
