from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL

_model = None

def get_embedding_model(model_name: str = None) -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(model_name or EMBEDDING_MODEL)
    return _model

def embed_texts(texts: list[str], model_name: str = None) -> list[list[float]]:
    model = get_embedding_model(model_name)
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()
