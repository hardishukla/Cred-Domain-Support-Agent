import re

def fixed_size_chunks(documents: list[dict], chunk_size: int = 200, overlap: int = 50) -> list[dict]:
    chunks = []
    for doc in documents:
        content = doc["content"]
        doc_id = doc["doc_id"]
        start = 0
        i = 0
        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk_text = content[start:end]
            chunks.append({
                "chunk_id": f"{doc_id}_fixed_{i}",
                "text": chunk_text,
                "parent_doc_id": doc_id,
                "strategy": "fixed"
            })
            if end == len(content):
                break
            start += chunk_size - overlap
            i += 1
    return chunks

def sentence_chunks(documents: list[dict], min_chunk_length: int = 50) -> list[dict]:
    chunks = []
    for doc in documents:
        content = doc["content"]
        doc_id = doc["doc_id"]
        
        # Split on newline or period followed by space and uppercase
        parts = re.split(r'(?<=\.)\s+(?=[A-Z])|\n+', content)
        
        i = 0
        current_chunk = ""
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if current_chunk:
                current_chunk += " " + part
            else:
                current_chunk = part
                
            if len(current_chunk) >= min_chunk_length:
                chunks.append({
                    "chunk_id": f"{doc_id}_sent_{i}",
                    "text": current_chunk,
                    "parent_doc_id": doc_id,
                    "strategy": "sentence"
                })
                current_chunk = ""
                i += 1
                
        if current_chunk:
            chunks.append({
                "chunk_id": f"{doc_id}_sent_{i}",
                "text": current_chunk,
                "parent_doc_id": doc_id,
                "strategy": "sentence"
            })
            
    return chunks
