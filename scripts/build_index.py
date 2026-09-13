import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.rag.loader import load_documents
from src.rag.chunking import fixed_size_chunks, sentence_chunks
from src.rag.indexing import build_index

def main():
    print("Loading documents...")
    docs = load_documents()
    print(f"Loaded {len(docs)} documents.")
    
    print("Generating fixed-size chunks...")
    fixed_chunks = fixed_size_chunks(docs)
    print(f"Generated {len(fixed_chunks)} fixed-size chunks.")
    
    print("Generating sentence-based chunks...")
    sent_chunks = sentence_chunks(docs)
    print(f"Generated {len(sent_chunks)} sentence-based chunks.")
    
    print("Embedding and indexing fixed chunks...")
    build_index(fixed_chunks, "kb_fixed_chunks")
    
    print("Embedding and indexing sentence chunks...")
    build_index(sent_chunks, "kb_sentence_chunks")
    
    print("Done. Indexing complete.")

if __name__ == "__main__":
    main()
