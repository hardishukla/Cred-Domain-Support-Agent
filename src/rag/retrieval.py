import chromadb
from src.rag.embeddings import embed_texts
from src.config import CHROMA_PERSIST_DIR

def retrieve(query: str, collection_name: str = "kb_fixed_chunks", top_k: int = 3, persist_dir: str = None) -> list[dict]:
    persist_dir = persist_dir or CHROMA_PERSIST_DIR
    client = chromadb.PersistentClient(path=persist_dir)
    try:
        collection = client.get_collection(name=collection_name)
    except Exception:
        return []

    query_embeddings = embed_texts([query])
    
    results = collection.query(
        query_embeddings=query_embeddings,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    formatted_results = []
    if not results["ids"] or not results["ids"][0]:
        return formatted_results
        
    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    
    for i in range(len(ids)):
        dist = distances[i]
        # Chroma default is L2. similarity = 1 / (1 + distance)
        similarity = 1.0 / (1.0 + dist)
        
        formatted_results.append({
            "chunk_id": ids[i],
            "chunk_text": documents[i],
            "parent_doc_id": metadatas[i]["parent_doc_id"],
            "metadata": metadatas[i],
            "similarity_score": similarity
        })
        
    formatted_results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return formatted_results
