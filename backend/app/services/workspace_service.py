from pathlib import Path
from uuid import uuid4

from app.config import get_settings

def create_workspace() -> tuple[str, Path]:
    """Create an isolated directory for a repository workspace."""
    settings = get_settings()
    workspace_id = str(uuid4())
    workspace_path = settings.workspace_root / workspace_id

    workspace_path.mkdir(parents=True, exist_ok=False)

    return workspace_id, workspace_path