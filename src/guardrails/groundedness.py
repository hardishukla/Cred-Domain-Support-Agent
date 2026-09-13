import re
from typing import Tuple

STOP_WORDS = {"a", "the", "is", "are", "in", "on", "of", "to", "and", "for", "with", "that", "this", "it"}

def tokenize(text: str) -> set[str]:
    # lowercase and split by non-alphanumeric
    words = re.findall(r'\b\w+\b', text.lower())
    return set(words) - STOP_WORDS

def check_groundedness(answer: str, context_chunks: list[str]) -> Tuple[bool, float]:
    """Check if the answer is grounded in the provided context.
    
    Returns (is_grounded, overlap_score).
    """
    if "I don't know" in answer:
        return True, 1.0
        
    answer_words = tokenize(answer)
    if not answer_words:
        return True, 1.0 # Edge case, no meaningful words
        
    context_text = " ".join(context_chunks)
    context_words = tokenize(context_text)
    
    overlap_count = len(answer_words & context_words)
    overlap_score = overlap_count / len(answer_words)
    
    return overlap_score >= 0.3, overlap_score
