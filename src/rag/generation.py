from src.config import MOCK_LLM, RAG_SIMILARITY_THRESHOLD

def generate_answer(query: str, retrieval_results: list[dict], threshold: float = None) -> dict:
    if threshold is None:
        threshold = RAG_SIMILARITY_THRESHOLD
        
    if not retrieval_results:
        return {
            "answer": "I don't know based on the available knowledge base.",
            "grounded": False,
            "sources": [],
            "similarity_scores": []
        }
        
    top_result = retrieval_results[0]
    top_sim = top_result["similarity_score"]
    
    scores = [r["similarity_score"] for r in retrieval_results]
    
    if MOCK_LLM:
        if top_sim >= threshold:
            sources = list(set([r["parent_doc_id"] for r in retrieval_results]))
            return {
                "answer": top_result["chunk_text"],
                "grounded": True,
                "sources": sources,
                "similarity_scores": scores
            }
        else:
            return {
                "answer": "I don't know based on the available knowledge base.",
                "grounded": False,
                "sources": [],
                "similarity_scores": scores
            }
    
    # Non-MOCK_LLM fallback (placeholder)
    return {
        "answer": "Not implemented",
        "grounded": False,
        "sources": [],
        "similarity_scores": scores
    }
