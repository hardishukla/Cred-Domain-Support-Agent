from src.agent.state import AgentState
from src.agent.router import classify_intent, extract_record_id
from src.rag.retrieval import retrieve
from src.rag.generation import generate_answer
from src.tools.loan_status import check_loan_application_status
from src.guardrails.pii import mask_pii
from src.guardrails.injection import detect_injection
from src.guardrails.groundedness import check_groundedness
from src.resilience.retry import with_retry
from src.resilience.timeouts import with_node_timeout

def input_guardrail_node(state: AgentState) -> dict:
    query = state.get("query", "")
    masked_query, pii_detected = mask_pii(query)
    is_injection, _ = detect_injection(masked_query)
    
    return {
        "masked_query": masked_query,
        "pii_detected": pii_detected,
        "injection_detected": is_injection,
        "intent": "refused" if is_injection else None
    }

def intent_router_node(state: AgentState) -> dict:
    if state.get("injection_detected"):
        return {"intent": "refused", "answer": "Request blocked due to policy violation.", "route": "refused"}
        
    intent = classify_intent(state.get("masked_query", ""))
    return {"intent": intent}

def rag_node(state: AgentState) -> dict:
    masked_query = state.get("masked_query", "")
    
    def retrieve_with_retry():
        return with_retry(lambda: retrieve(masked_query))
    
    results = with_node_timeout(retrieve_with_retry, timeout_seconds=10)
    
    def generate_with_retry():
        return with_retry(lambda: generate_answer(masked_query, results, threshold=0.4089))
        
    answer_dict = with_node_timeout(generate_with_retry, timeout_seconds=10)
    
    context_chunks = [r["chunk_text"] for r in results]
    is_grounded, score = check_groundedness(answer_dict["answer"], context_chunks)
    
    # If not grounded, fallback
    if not is_grounded:
        final_answer = "I don't know based on the available knowledge base."
    else:
        final_answer = answer_dict["answer"]
        
    return {
        "retrieval_results": results,
        "answer": final_answer,
        "grounded": is_grounded,
        "sources": answer_dict.get("sources", []),
        "route": "rag"
    }

def loan_status_node(state: AgentState) -> dict:
    masked_query = state.get("masked_query", "")
    record_id = extract_record_id(masked_query)
    
    if not record_id:
        return {
            "error": "No loan ID found in query.",
            "answer": "Could you please provide your LOAN ID?",
            "route": "loan_status"
        }
        
    def check_status_with_retry():
        return with_retry(lambda: check_loan_application_status(record_id))
        
    result = with_node_timeout(check_status_with_retry, timeout_seconds=10)
    
    if "error" in result:
        return {
            "tool_result": result,
            "answer": f"Sorry, we couldn't find a loan application for {record_id}.",
            "route": "loan_status",
            "grounded": True,
            "sources": ["loan_applications"]
        }
        
    formatted_answer = (
        f"Loan {result['record_id']} status is {result['status']}. "
        f"Category: {result['category']}. Amount: {result['loan_amount_inr']} INR."
    )
    
    return {
        "tool_result": result,
        "answer": formatted_answer,
        "route": "loan_status",
        "escalation_score": result.get("escalation_score"),
        "escalation_flag": result.get("escalation_flag"),
        "grounded": True,
        "sources": ["loan_applications"]
    }

def output_node(state: AgentState) -> dict:
    return {
        "answer": state.get("answer", "No answer generated.")
    }
