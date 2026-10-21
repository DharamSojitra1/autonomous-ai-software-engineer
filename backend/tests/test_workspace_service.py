
from pathlib import Path

from app.config import get_settings
from app.services.workspace_service import create_workspace


def test_create_workspace_creates_directory(tmp_path: Path, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "workspace_root", tmp_path)

    workspace_id, workspace_path = create_workspace()

    assert workspace_id
    assert workspace_path == tmp_path / workspace_id
    assert workspace_path.is_dir()


def test_create_workspace_generates_unique_ids(tmp_path: Path, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "workspace_root", tmp_path)

    first_id, first_path = create_workspace()
    second_id, second_path = create_workspace()

    assert first_id != second_id
    assert first_path != second_path
    assert first_path.is_dir()
    assert second_path.is_dir()

