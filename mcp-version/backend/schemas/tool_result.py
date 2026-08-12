from pydantic import BaseModel

class Source(BaseModel):
    type: str

    # for type document
    documentId: str | None = None
    documentName: str | None = None
    fileName: str | None = None
    page: int | None = None
    text: str | None = None

    # for type web
    title: str | None = None
    url: str | None = None

    # for type image
    path: str | None = None

class ToolResult(BaseModel):
    llm_context: str
    sources: list[Source]