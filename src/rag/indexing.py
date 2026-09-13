import chromadb
from src.rag.embeddings import embed_texts
from src.config import CHROMA_PERSIST_DIR

def build_index(chunks: list[dict], collection_name: str, persist_dir: str = None) -> None:
    persist_dir = persist_dir or CHROMA_PERSIST_DIR
    client = chromadb.PersistentClient(path=persist_dir)
    
    collection = client.get_or_create_collection(name=collection_name)
    
    if not chunks:
        return
        
    chunk_ids = [c["chunk_id"] for c in chunks]
    chunk_texts = [c["text"] for c in chunks]
    metadatas = [{"parent_doc_id": c["parent_doc_id"], "strategy": c["strategy"]} for c in chunks]
    
    embeddings = embed_texts(chunk_texts)
    
    collection.upsert(
        ids=chunk_ids,
        documents=chunk_texts,
        embeddings=embeddings,
        metadatas=metadatas
    )
