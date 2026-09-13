import re
from typing import Tuple

def mask_pii(text: str) -> Tuple[str, list[str]]:
    """Mask PII patterns in text. Returns (masked_text, list_of_detected_pii_types)."""
    detected_types = []
    
    # 1. Aadhaar
    aadhaar_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
    if re.search(aadhaar_pattern, text):
        detected_types.append("AADHAAR")
        text = re.sub(aadhaar_pattern, "[AADHAAR_MASKED]", text)
        
    # 2. PAN
    pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'
    if re.search(pan_pattern, text):
        detected_types.append("PAN")
        text = re.sub(pan_pattern, "[PAN_MASKED]", text)
        
    # 3. Account number
    # Processed after Aadhaar
    acct_context = re.search(r'\b(account|a/c|acct)\b', text, re.IGNORECASE)
    if acct_context:
        acct_pattern = r'\b\d{9,18}\b'
        if re.search(acct_pattern, text):
            detected_types.append("ACCOUNT")
            text = re.sub(acct_pattern, "[ACCOUNT_MASKED]", text)
            
    return text, detected_types
