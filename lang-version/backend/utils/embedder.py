from langchain_huggingface import HuggingFaceEmbeddings

model = None

def get_model():
    global model

    print("🔥 get_model() CALLED")

    if model is None:
        print("Loading Embedding Model...")

        # Limit torch's internal thread pool - reduces resident memory used
        # by the BLAS/OMP threads without changing embedding output.
        import torch
        torch.set_num_threads(1)

        model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={
                "device": "cpu"
            },
            encode_kwargs={
                "normalize_embeddings": True
            }
        )

        print("Embedding Model Loaded!")

    return model


def create_embeddings(texts: list[str]) -> list[list]:
    model = get_model()
    return model.embed_documents(texts)


def create_embedding(text: str) -> list:
    model = get_model()
    return model.embed_query(text)