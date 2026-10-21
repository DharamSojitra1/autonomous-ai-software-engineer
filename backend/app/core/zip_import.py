from pathlib import Path, PurePosixPath, PureWindowsPath
from stat import S_ISLNK
from zipfile import BadZipFile, ZipFile

from app.config import get_settings

class ArchiveValidationError(ValueError):
    """Raised when an uploaded archive violates workspace safety rules."""

def validate_archive(archive: ZipFile) -> list:
    settings = get_settings()
    entries = archive.infolist()

    if not entries:
        raise ArchiveValidationError("The ZIP archive is empty.")

    if len(entries) > settings.max_archive_files:
        raise ArchiveValidationError("The archive contains too many entries.")

    max_expanded = settings.max_extracted_size_mb * 1024 * 1024
    total_expanded = 0
    seen_paths: set[str] = set()

    for entry in entries:
        name = entry.filename

        if not name or "\x00" in name or "\\" in name:
            raise ArchiveValidationError("The archive contains an invalid path.")

        posix_name = PurePosixPath(name)
        windows_name = PureWindowsPath(name)

        if(
            posix_name.is_absolute()
            or windows_name.is_absolute()
            or windows_name.drive
            or any(part in ("", ".", "..") for part in name.rstrip("/").split("/"))
        ):
            raise ArchiveValidationError("The archive contains an unsafe path.")

        normalized = name.rstrip("/")
        if normalized in seen_paths:
            raise ArchiveValidationError("The archive contains duplicate paths.")

        seen_paths.add(normalized)

        unix_mode = entry.external_attr >> 16
        if S_ISLNK(unix_mode):
            raise ArchiveValidationError("Symbolic links are not allowed.")

        if entry.flag_bits & 0x1:
            raise ArchiveValidationError("Encrypted ZIP entries are not supported.")

        if entry.file_size < 0:
            raise ArchiveValidationError("The archive contains invalid file metadata.")

        total_expanded += entry.file_size

        if total_expanded > max_expanded:
            raise ArchiveValidationError(
                "The extracted archive would exceed the allowed size."
            )
        
    return entries

def extract_archive(archive: ZipFile, entries: list, workspace: Path) -> None:
    root = workspace.resolve()

    for entry in entries:
        relative = PurePosixPath(entry.filename)
        destination = (root / Path(*relative.parts)).resolve()

        if not destination.is_relative_to(root):
            raise ArchiveValidationError("The archive contains an unsafe path.")
        
        if entry.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)

        with archive.open(entry, "r") as source, destination.open("xb") as target:
            while chunk := source.read(64 * 1024):
                target.write(chunk)