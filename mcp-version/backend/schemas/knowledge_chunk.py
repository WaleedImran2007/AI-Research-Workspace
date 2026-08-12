from pydantic import BaseModel

class KnowledgeChunkCreate(BaseModel):
    ownerId: str
    collectionId: str
    documentId: str

    chunkIndex: int
    text: str

    emdeddings: list[float]

class KnowledgeChunkResponse(BaseModel):
    id: str
    ownerId: str
    collectionId: str
    documentId: str

    chunkIndex: int

    text: str

    embedding: list[float]