from sentence_transformers import SentenceTransformer

model = None

def get_model():
    global model
    if model is None:
        print("Loading Model...")
        model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        print("Model Loaded Successfully!")

    return model

def create_embedding(text: str) -> list:
    model = get_model()
    return model.encode(
        text,
        normalize_embeddings=True,
    ).tolist()