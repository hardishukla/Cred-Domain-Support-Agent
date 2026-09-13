import re

def classify_intent(query: str) -> str:
    """Classify user intent as loan_status or rag based on keywords/patterns."""
    query_lower = query.lower()
    
    # Check for LOAN ID pattern
    if re.search(r"loan-\d{4}", query_lower):
        return "loan_status"
        
    # Check for keywords
    keywords = ["status", "application status", "check application", "my application", "loan status"]
    if any(keyword in query_lower for keyword in keywords):
        return "loan_status"
        
    return "rag"

def extract_record_id(query: str) -> str | None:
    """Extract a loan record ID from a query if present."""
    match = re.search(r"LOAN-\d{4}", query, re.IGNORECASE)
    if match:
        return match.group(0).upper()
    return None
