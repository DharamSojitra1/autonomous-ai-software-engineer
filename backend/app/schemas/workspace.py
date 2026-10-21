from pydantic import BaseModel, ConfigDict

class WorkspaceCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workspace_id: str
    status: str