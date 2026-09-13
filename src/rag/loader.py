import os
import glob
from pathlib import Path
from src.config import KB_DIR

def load_documents(kb_dir: str = None) -> list[dict]:
    dir_path = kb_dir or KB_DIR
    documents = []
    
    if not os.path.exists(dir_path):
        return documents
        
    for filepath in glob.glob(os.path.join(dir_path, "*.md")):
        path = Path(filepath)
        stem = path.stem
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                continue
            title = lines[0].strip()
            content = "".join(lines)
            
        documents.append({
            "doc_id": stem,
            "title": title,
            "content": content
        })
        
    return documents
