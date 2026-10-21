
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

client = TestClient(app)


def test_create_workspace_endpoint(tmp_path, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "workspace_root", tmp_path)

    response = client.post("/api/v1/workspaces")

    assert response.status_code == 201

    data = response.json()
    assert data["status"] == "created"
    assert data["workspace_id"]

    workspace_path = tmp_path / data["workspace_id"]
    assert workspace_path.is_dir()
