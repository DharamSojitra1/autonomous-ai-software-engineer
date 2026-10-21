from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


def test_list_workspace_files_api(tmp_path: Path, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "workspace_root", tmp_path)

    workspace_id = str(uuid4())
    workspace = tmp_path / workspace_id
    workspace.mkdir()
    (workspace / "main.py").write_text("print('hello')\n", encoding="utf-8")

    client = TestClient(app)
    response = client.get(f"/api/v1/workspaces/{workspace_id}/files")

    assert response.status_code == 200
    data = response.json()
    assert data["workspace_id"] == workspace_id
    assert "main.py" in data["files"]
    assert data["total"] == 1


def test_read_workspace_file_api(tmp_path: Path, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "workspace_root", tmp_path)

    workspace_id = str(uuid4())
    workspace = tmp_path / workspace_id
    workspace.mkdir()
    (workspace / "main.py").write_text("print('hello')\n", encoding="utf-8")

    client = TestClient(app)
    response = client.get(
        f"/api/v1/workspaces/{workspace_id}/file",
        params={"path": "main.py"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["path"] == "main.py"
    assert data["content"] == "print('hello')\n"
    assert data["size_bytes"] == len("print('hello')\n".encode("utf-8"))


def test_search_workspace_code_api(tmp_path: Path, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "workspace_root", tmp_path)

    workspace_id = str(uuid4())
    workspace = tmp_path / workspace_id
    workspace.mkdir()
    (workspace / "main.py").write_text(
        "def calculate():\n    return 42\n",
        encoding="utf-8",
    )

    client = TestClient(app)
    response = client.get(
        f"/api/v1/workspaces/{workspace_id}/search",
        params={"q": "return 42"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["results"][0]["path"] == "main.py"
    assert data["results"][0]["line"] == 2


def test_workspace_api_returns_404_for_missing_workspace(
    tmp_path: Path,
    monkeypatch,
):
    settings = get_settings()
    monkeypatch.setattr(settings, "workspace_root", tmp_path)

    client = TestClient(app)
    response = client.get(f"/api/v1/workspaces/{uuid4()}/files")

    assert response.status_code == 404


def test_workspace_api_rejects_invalid_workspace_id():
    client = TestClient(app)
    response = client.get("/api/v1/workspaces/not-a-uuid/files")

    assert response.status_code == 400
