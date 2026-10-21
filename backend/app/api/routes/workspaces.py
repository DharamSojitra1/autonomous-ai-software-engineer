from fastapi import APIRouter, HTTPException, status, File, UploadFile, Query
from app.services.workspace_service import create_workspace
from zipfile import BadZipFile, ZipFile
from app.config import get_settings
from app.core.zip_import import validate_archive, extract_archive, ArchiveValidationError
from pathlib import Path
from uuid import UUID
from app.schemas.workspace import (
    WorkspaceCreateResponse,
    WorkspaceFilesResponse,
    WorkspaceFileResponse,
    CodeSearchResponse,
)
from app.services.repository_service import (
    list_repository_files,
    read_repository_file,
    search_repository_code,
)

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

@router.post(
    "",
    response_model=WorkspaceCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace_endpoint() -> WorkspaceCreateResponse:
    try:
        workspace_id, workspace_path = create_workspace()
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create workspace.",
        ) from exc

    return WorkspaceCreateResponse(
        workspace_id=workspace_id,
        status="created",
    )


@router.post(
    "/upload",
    response_model=WorkspaceCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_workspace(file: UploadFile = File(...)) -> WorkspaceCreateResponse:
    import shutil

    settings = get_settings()
    workspace_id: str | None = None
    workspace_path = None

    try:
        if not file.filename or not file.filename.lower().endswith(".zip"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Upload a ZIP file.",
            )

        file.file.seek(0, 2)
        upload_size = file.file.tell()
        file.file.seek(0)

        max_bytes = settings.max_upload_size_mb * 1024 * 1024
        if upload_size == 0 or upload_size > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="The uploaded file is empty or exceeds the size limit.",
            )

        with ZipFile(file.file) as archive:
            entries = validate_archive(archive)
            workspace_id, workspace_path = create_workspace()
            extract_archive(archive, entries, workspace_path)

    except HTTPException:
        raise
    except (BadZipFile, ArchiveValidationError) as exc:
        if workspace_path is not None:
            shutil.rmtree(workspace_path, ignore_errors=True)

        detail = (
            str(exc)
            if isinstance(exc, ArchiveValidationError)
            else "The uploaded ZIP file is invalid."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        ) from exc
    except OSError as exc:
        if workspace_path is not None:
            shutil.rmtree(workspace_path, ignore_errors=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not process the uploaded repository.",
        ) from exc
    finally:
        file.file.close()

    return WorkspaceCreateResponse(
        workspace_id=workspace_id,
        status="created",
    )


def get_workspace_path(workspace_id: str) -> Path:
    """Resolve and validate a workspace ID against the configured root."""
    try:
        parsed_id = UUID(workspace_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid workspace ID.",
        ) from exc

    root = get_settings().workspace_root.resolve()
    workspace_path = (root / str(parsed_id)).resolve()

    if not workspace_path.is_relative_to(root):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid workspace path.",
        )

    if not workspace_path.is_dir():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found.",
        )

    return workspace_path


@router.get(
    "/{workspace_id}/files",
    response_model=WorkspaceFilesResponse,
)
def list_workspace_files_endpoint(
    workspace_id: str,
) -> WorkspaceFilesResponse:
    workspace_path = get_workspace_path(workspace_id)

    try:
        files = list_repository_files(workspace_path)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not list repository files.",
        ) from exc

    return WorkspaceFilesResponse(
        workspace_id=workspace_id,
        files=files,
        total=len(files),
    )


@router.get(
    "/{workspace_id}/file",
    response_model=WorkspaceFileResponse,
)
def read_workspace_file_endpoint(
    workspace_id: str,
    path: str = Query(..., min_length=1, max_length=1024),
) -> WorkspaceFileResponse:
    workspace_path = get_workspace_path(workspace_id)

    try:
        content = read_repository_file(workspace_path, path)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not read repository file.",
        ) from exc

    return WorkspaceFileResponse(
        workspace_id=workspace_id,
        path=path,
        content=content,
        size_bytes=len(content.encode("utf-8")),
    )


@router.get(
    "/{workspace_id}/search",
    response_model=CodeSearchResponse,
)
def search_workspace_code_endpoint(
    workspace_id: str,
    q: str = Query(..., min_length=1, max_length=500),
) -> CodeSearchResponse:
    workspace_path = get_workspace_path(workspace_id)

    try:
        results = search_repository_code(workspace_path, q)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not search repository code.",
        ) from exc

    return CodeSearchResponse(
        workspace_id=workspace_id,
        query=q,
        total=len(results),
        results=results,
    )

