from pydantic import BaseModel, Field


class Source(BaseModel):
    type: str

    # for type document
    documentId: str | None = None
    documentName: str | None = None
    fileName: str | None = None
    documentType: str | None = None  # "pdf" or "audio" - lets the frontend pick the right card/viewer
    page: int | None = None
    startTime: float | None = None  # audio chunks only - seconds into the file
    text: str | None = None

    # for type web
    title: str | None = None
    url: str | None = None

    # for type image
    path: str | None = None

class ToolFile(BaseModel):
    filename: str
    file_type: str
    storage_path: str

class ToolResult(BaseModel):
    llm_context: str
    sources: list[Source] = Field(default_factory=list)
    file: ToolFile | None = None