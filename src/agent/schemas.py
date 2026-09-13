from pydantic import BaseModel, Field
from typing import Optional
import uuid

class AgentResponse(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: str
    answer: str
    route: str  # "rag" | "loan_status" | "refused"
    grounded: bool = True
    sources: list[str] = Field(default_factory=list)
    escalation_score: Optional[float] = None
    escalation_flag: Optional[bool] = None
    error: Optional[str] = None
    thread_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "trace_id": "abc-123",
                "query": "What is EMI?",
                "answer": "EMI is calculated using...",
                "route": "rag",
                "grounded": True,
                "sources": ["emi_rules"],
            }
        }

def build_response(state: dict, query: str, thread_id: str = None, trace_id: str = None) -> AgentResponse:
    return AgentResponse(
        trace_id=trace_id or str(uuid.uuid4()),
        query=query,
        answer=state.get("answer", "No answer generated."),
        route=state.get("route", "unknown"),
        grounded=state.get("grounded", False),
        sources=state.get("sources", []),
        escalation_score=state.get("escalation_score"),
        escalation_flag=state.get("escalation_flag"),
        error=state.get("error"),
        thread_id=thread_id,
    )
