from pathlib import Path

from app.services.repository_service import search_repository_code


def search_code(
    workspace_path: Path,
    query: str,
    *,
    case_sensitive: bool = False,
) -> list[dict[str, str | int]]:
    """Search repository text for a literal query."""
    return search_repository_code(
        workspace_path,
        query,
        case_sensitive=case_sensitive,
    )
