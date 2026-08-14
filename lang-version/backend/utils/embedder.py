import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

client = InferenceClient(
    token = os.getenv("HF_TOKEN")
)

MODEL_NAME = "BAAI/bge-small-en-v1.5"

def create_embeddings(texts: list[str]) -> list[list]:
    if not texts:
        return []

    embeddings = client.feature_extraction(
        texts,
        model=MODEL_NAME,
    )

    return [embedding.tolist() for embedding in embeddings]


def create_embedding(text: str) -> list:
    if not text.strip():
        return []

    return client.feature_extraction(
        text,
        model=MODEL_NAME,
    ).tolist()