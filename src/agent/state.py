from typing import TypedDict, Optional, List

class AgentState(TypedDict, total=False):
    query: str
    masked_query: str
    intent: str                    # "rag" | "loan_status" | "refused"
    retrieval_results: list
    tool_result: dict
    answer: str
    grounded: bool
    sources: list
    route: str
    thread_id: str
    conversation_history: list
    error: str
    escalation_score: float
    escalation_flag: bool
    injection_detected: bool
    pii_detected: list
