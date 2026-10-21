
from io import BytesIO
from zipfile import ZipFile

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

client = TestClient(app)


def make_zip(files: dict[str, str]) -> bytes:
    buffer = BytesIO()

    with ZipFile(buffer, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)

    return buffer.getvalue()


def test_upload_valid_zip(tmp_path, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "workspace_root", tmp_path)

    archive_bytes = make_zip({"src/main.py": "print('hello')\n"})

    response = client.post(
        "/api/v1/workspaces/upload",
        files={
            "file": (
                "repository.zip",
                archive_bytes,
                "application/zip",
            )
        },
    )

    assert response.status_code == 201

    workspace_id = response.json()["workspace_id"]
    extracted_file = tmp_path / workspace_id / "src" / "main.py"

    assert extracted_file.read_text(encoding="utf-8") == "print('hello')\n"


def test_upload_invalid_zip_returns_400(tmp_path, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "workspace_root", tmp_path)

    response = client.post(
        "/api/v1/workspaces/upload",
        files={
            "file": (
                "broken.zip",
                b"this is not a zip archive",
                "application/zip",
            )
        },
    )

    assert response.status_code == 400
    assert list(tmp_path.iterdir()) == []


def test_upload_rejects_path_traversal(tmp_path, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "workspace_root", tmp_path)

    archive_bytes = make_zip({"../outside.txt": "malicious content"})

    response = client.post(
        "/api/v1/workspaces/upload",
        files={
            "file": (
                "malicious.zip",
                archive_bytes,
                "application/zip",
            )
        },
    )

    assert response.status_code == 400
    assert not (tmp_path.parent / "outside.txt").exists()
    assert list(tmp_path.iterdir()) == []
