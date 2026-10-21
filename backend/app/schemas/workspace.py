from pydantic import BaseModel, ConfigDict

class WorkspaceCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workspace_id: str
    status: str

class WorkspaceFilesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workspace_id: str
    files: list[str]
    total: int


class WorkspaceFileResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workspace_id: str
    path: str
    content: str
    size_bytes: int


class CodeSearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    line: int
    text: str


class CodeSearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workspace_id: str
    query: str
    total: int
    results: list[CodeSearchResult]
