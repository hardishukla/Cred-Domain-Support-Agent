from fastapi import APIRouter, HTTPException, BackgroundTasks
from src.api.models import ChatRequest
from src.agent.schemas import AgentResponse, build_response
from src.agent.graph import run_agent
from src.api.logging import log_request_response
from src.resilience.checkpointing import get_checkpointer
import uuid

router = APIRouter()
checkpointer = get_checkpointer()

@router.get("/health")
async def health_endpoint():
    return {"status": "ok"}

@router.post("/chat", response_model=AgentResponse)
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    trace_id = str(uuid.uuid4())
    try:
        # Run agent graph with checkpointer
        state = run_agent(request.query, thread_id=request.thread_id, checkpointer=checkpointer)
        response = build_response(state, query=request.query, thread_id=request.thread_id, trace_id=trace_id)
        
        # Background logging
        background_tasks.add_task(
            log_request_response,
            trace_id,
            request.model_dump(),
            response.model_dump(),
            "/chat"
        )
        return response
    except Exception as e:
        error_resp = AgentResponse(
            trace_id=trace_id,
            query=request.query,
            answer="Internal server error.",
            route="error",
            error=str(e),
            thread_id=request.thread_id
        )
        raise HTTPException(status_code=500, detail=error_resp.model_dump())
