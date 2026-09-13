from src.rag.retrieval import retrieve

def calibrate_threshold(in_scope_queries: list[str], out_of_scope_queries: list[str], collection_name: str = "kb_fixed_chunks", persist_dir: str = None) -> dict:
    in_scope_similarities = {}
    out_of_scope_similarities = {}
    
    for q in in_scope_queries:
        res = retrieve(q, collection_name=collection_name, top_k=1, persist_dir=persist_dir)
        in_scope_similarities[q] = res[0]["similarity_score"] if res else 0.0
        
    for q in out_of_scope_queries:
        res = retrieve(q, collection_name=collection_name, top_k=1, persist_dir=persist_dir)
        out_of_scope_similarities[q] = res[0]["similarity_score"] if res else 0.0
        
    min_in_scope = min(in_scope_similarities.values()) if in_scope_similarities else 0.0
    max_out_of_scope = max(out_of_scope_similarities.values()) if out_of_scope_similarities else 0.0
    
    selected_threshold = (min_in_scope + max_out_of_scope) / 2.0
    
    return {
        "in_scope_similarities": in_scope_similarities,
        "out_of_scope_similarities": out_of_scope_similarities,
        "min_in_scope": min_in_scope,
        "max_out_of_scope": max_out_of_scope,
        "selected_threshold": selected_threshold,
        "reasoning": f"Midpoint between max out-of-scope ({max_out_of_scope:.4f}) and min in-scope ({min_in_scope:.4f})"
    }

def evaluate_chunking(queries: list[dict], collection_name: str, top_k: int = 3, persist_dir: str = None) -> dict:
    results = []
    p_sum = 0.0
    r_sum = 0.0
    
    for q_data in queries:
        query = q_data["query"]
        relevant_docs = set(q_data["relevant_docs"])
        
        retrieved = retrieve(query, collection_name=collection_name, top_k=top_k, persist_dir=persist_dir)
        retrieved_docs = list(set([r["parent_doc_id"] for r in retrieved]))
        
        intersection = set(retrieved_docs).intersection(relevant_docs)
        
        precision = len(intersection) / len(retrieved_docs) if retrieved_docs else 0.0
        recall = len(intersection) / len(relevant_docs) if relevant_docs else 1.0 if not retrieved_docs else 0.0
        
        results.append({
            "query": query,
            "precision_at_k": precision,
            "recall_at_k": recall,
            "retrieved_docs": retrieved_docs
        })
        
        p_sum += precision
        r_sum += recall
        
    mean_p = p_sum / len(queries) if queries else 0.0
    mean_r = r_sum / len(queries) if queries else 0.0
    
    return {
        "query_results": results,
        "mean_precision": mean_p,
        "mean_recall": mean_r
    }

import re

def _tokenize(text: str) -> set[str]:
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = set(text.split())
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "to", "in", "for", "of", "on", "with", "at", "by", "from", "and", "or", "but", "what", "how", "why", "when", "where", "it", "this", "that", "i", "you", "he", "she", "they", "we", "my", "your", "do", "does", "did", "can", "could", "would", "should", "tell", "me", "about"}
    return words - stop_words

def context_relevance(query: str, retrieved_chunks: list[str]) -> float:
    """Score how relevant the retrieved context is to the query.
    MOCK_LLM strategy: word-overlap between query and chunks, normalized to [0,1]."""
    query_words = _tokenize(query)
    if not query_words:
        return 0.0
    context_words = set()
    for chunk in retrieved_chunks:
        context_words.update(_tokenize(chunk))
    score = len(query_words & context_words) / len(query_words)
    return min(max(score, 0.0), 1.0)

def groundedness_score(answer: str, context_chunks: list[str]) -> float:
    """Score how grounded the answer is in the context.
    MOCK_LLM strategy: word-overlap between answer and context."""
    if "I don't know" in answer:
        return 1.0
    
    answer_words = _tokenize(answer)
    if not answer_words:
        return 0.0
    context_words = set()
    for chunk in context_chunks:
        context_words.update(_tokenize(chunk))
    score = len(answer_words & context_words) / len(answer_words)
    return min(max(score, 0.0), 1.0)

def answer_relevance(query: str, answer: str) -> float:
    """Score how relevant the answer is to the query.
    MOCK_LLM strategy: word-overlap between query and answer."""
    query_words = _tokenize(query)
    if not query_words:
        return 0.0
    answer_words = _tokenize(answer)
    score = len(query_words & answer_words) / len(query_words)
    return min(max(score, 0.0), 1.0)

def run_triad_evaluation(queries: list[dict], collection_name: str = "kb_fixed_chunks", persist_dir: str = None) -> dict:
    """Run full triad evaluation on a list of queries."""
    from src.rag.retrieval import retrieve
    from src.rag.generation import generate_answer
    
    results = []
    cr_sum = 0.0
    g_sum = 0.0
    ar_sum = 0.0
    
    for q_data in queries:
        query = q_data["query"]
        retrieved = retrieve(query, collection_name=collection_name, top_k=3, persist_dir=persist_dir)
        context_chunks = [r["chunk_text"] for r in retrieved]
        
        answer_data = generate_answer(query, retrieved, threshold=0.3)
        answer = answer_data["answer"]
        
        cr = context_relevance(query, context_chunks)
        g = groundedness_score(answer, context_chunks)
        ar = answer_relevance(query, answer)
        
        cr_sum += cr
        g_sum += g
        ar_sum += ar
        
        results.append({
            "query": query,
            "topic": q_data.get("topic", "unknown"),
            "context_relevance": cr,
            "groundedness": g,
            "answer_relevance": ar,
            "answer": answer
        })
        
    num = len(queries)
    return {
        "query_results": results,
        "mean_context_relevance": cr_sum / num if num > 0 else 0.0,
        "mean_groundedness": g_sum / num if num > 0 else 0.0,
        "mean_answer_relevance": ar_sum / num if num > 0 else 0.0
    }

