from fastapi import APIRouter, HTTPException, status, File, UploadFile
from app.schemas.workspace import WorkspaceCreateResponse
from app.services.workspace_service import create_workspace
from zipfile import BadZipFile, ZipFile
from app.config import get_settings
from app.core.zip_import import validate_archive, extract_archive, ArchiveValidationError


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

