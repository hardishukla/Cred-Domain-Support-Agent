import re
from typing import Tuple

def detect_injection(text: str) -> Tuple[bool, str | None]:
    """Detect prompt injection attempts. Returns (is_injection, matched_pattern)."""
    patterns = [
        r"ignore previous instructions",
        r"ignore all previous",
        r"disregard above",
        r"disregard previous",
        r"forget your instructions",
        r"reveal system prompt",
        r"show system prompt",
        r"expose internal",
        r"bypass rules",
        r"bypass security",
        r"override security",
        r"override instructions",
        r"you are now",
        r"act as if",
        r"pretend you are",
        r"ignore safety"
    ]
    
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True, pattern
            
    return False, None
