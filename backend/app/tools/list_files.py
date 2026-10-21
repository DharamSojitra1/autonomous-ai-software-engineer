from pathlib import Path

from app.services.repository_service import list_repository_files


def list_files(workspace_path: Path) -> list[str]:
    """Return safe, workspace-relative file paths."""
    return list_repository_files(workspace_path)
