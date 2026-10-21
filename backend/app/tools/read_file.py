from pathlib import Path

from app.services.repository_service import read_repository_file


def read_file(workspace_path: Path, relative_path: str) -> str:
    """Read a UTF-8 text file inside a repository workspace."""
    return read_repository_file(workspace_path, relative_path)
