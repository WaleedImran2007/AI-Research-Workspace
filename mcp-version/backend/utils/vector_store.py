from langchain_mongodb import MongoDBAtlasVectorSearch

from database import knowledge_chunks_collection
from utils.embedder import get_model

embeddings = get_model()

vector_store = MongoDBAtlasVectorSearch(
    collection=knowledge_chunks_collection,
    embedding=embeddings,
    index_name="vector_index",
    text_key="text",
    embedding_key="embedding",
)