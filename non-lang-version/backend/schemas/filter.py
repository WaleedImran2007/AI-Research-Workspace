from pydantic import BaseModel

class FilterSchema(BaseModel):
    query: str

    document_names: list[str] = []
    collection_names: list[str] = []

    document_ids: list[str] = []
    collection_ids: list[str] = []

    pages: list[int] = []