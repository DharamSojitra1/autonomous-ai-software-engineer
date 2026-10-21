from pathlib import Path, PureWindowsPath

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
}

IGNORED_FILES = {
    ".env",
    ".env.local",
    ".env.production",
}


class UnsafeRepositoryPathError(ValueError):
    """Raised when a requested path is unsafe or escapes the workspace."""


def resolve_workspace_path(workspace: Path, relative_path: str = ".") -> Path:
    """Resolve a workspace-relative path while rejecting symlinks and escapes."""
    root = workspace.resolve()

    if not root.is_dir():
        raise FileNotFoundError("Workspace does not exist.")

    if not relative_path or "\\" in relative_path:
        raise UnsafeRepositoryPathError("Invalid repository path.")

    windows_path = PureWindowsPath(relative_path)
    requested = Path(relative_path)

    if (
        requested.is_absolute()
        or windows_path.is_absolute()
        or windows_path.drive
        or ".." in requested.parts
    ):
        raise UnsafeRepositoryPathError("Invalid repository path.")

    candidate = root

    for part in requested.parts:
        if part in ("", "."):
            continue

        candidate = candidate / part

        # Check each original path component before resolving it.
        if candidate.is_symlink():
            raise UnsafeRepositoryPathError(
                "Symbolic links cannot be accessed."
            )

    resolved = candidate.resolve()

    if not resolved.is_relative_to(root):
        raise UnsafeRepositoryPathError("Path is outside the workspace.")

    return resolved


def list_repository_files(workspace: Path) -> list[str]:
    root = workspace.resolve()

    if not root.is_dir():
        raise FileNotFoundError("Workspace does not exist.")

    files: list[str] = []

    for path in root.rglob("*"):
        relative = path.relative_to(root)

        if any(part in IGNORED_DIRS for part in relative.parts):
            continue

        if path.name in IGNORED_FILES or path.is_symlink():
            continue

        try:
            resolved = path.resolve(strict=True)
            if not resolved.is_relative_to(root):
                continue
        except (OSError, RuntimeError):
            continue

        if resolved.is_file():
            files.append(relative.as_posix())

    return sorted(files)


def read_repository_file(workspace: Path, relative_path: str) -> str:
    from app.config import get_settings

    target = resolve_workspace_path(workspace, relative_path)

    if not target.is_file():
        raise FileNotFoundError("File does not exist.")

    relative = target.relative_to(workspace.resolve())

    if relative.name in IGNORED_FILES:
        raise UnsafeRepositoryPathError(
            "This file is not available for reading."
        )

    if any(part in IGNORED_DIRS for part in relative.parts):
        raise UnsafeRepositoryPathError(
            "This file is not available for reading."
        )

    settings = get_settings()
    max_bytes = settings.max_read_file_size_kb * 1024

    if max_bytes < 1:
        raise ValueError("Read file size limit must be positive.")

    if target.stat().st_size > max_bytes:
        raise ValueError("File exceeds the maximum read size.")

    try:
        return target.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("File is not valid UTF-8 text.") from exc


def search_repository_code(
    workspace: Path,
    query: str,
    *,
    case_sensitive: bool = False,
) -> list[dict[str, str | int]]:
    """Search text files and return bounded, workspace-relative matches."""
    from app.config import get_settings

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    settings = get_settings()
    max_results = settings.max_search_results
    max_bytes = settings.max_search_file_size_kb * 1024

    if max_results < 1 or max_bytes < 1:
        raise ValueError("Search limits must be positive.")

    root = workspace.resolve()

    if not root.is_dir():
        raise FileNotFoundError("Workspace does not exist.")

    results: list[dict[str, str | int]] = []
    needle = query if case_sensitive else query.casefold()

    for relative_path in list_repository_files(root):
        try:
            candidate = resolve_workspace_path(root, relative_path)

            if not candidate.is_file():
                continue

            if candidate.stat().st_size > max_bytes:
                continue

            content = candidate.read_text(encoding="utf-8")
        except (
            OSError,
            UnicodeDecodeError,
            RuntimeError,
            UnsafeRepositoryPathError,
        ):
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):
            haystack = line if case_sensitive else line.casefold()

            if needle in haystack:
                results.append(
                    {
                        "path": relative_path,
                        "line": line_number,
                        "text": line[:500],
                    }
                )

                if len(results) >= max_results:
                    return results

    return results
