from langgraph.graph import StateGraph, START, END
from src.agent.state import AgentState
from src.agent.nodes import (
    input_guardrail_node,
    intent_router_node,
    rag_node,
    loan_status_node,
    output_node,
)
from src.agent.memory import ConversationMemory

def route_by_intent(state: AgentState) -> str:
    intent = state.get("intent", "rag")
    if intent == "loan_status":
        return "loan_status"
    if intent == "refused":
        return "refused"
    return "rag"

def build_graph() -> StateGraph:
    builder = StateGraph(AgentState)
    builder.add_node("input_guardrail", input_guardrail_node)
    builder.add_node("intent_router", intent_router_node)
    builder.add_node("rag", rag_node)
    builder.add_node("loan_status", loan_status_node)
    builder.add_node("output", output_node)
    
    # Simple output node for refused
    builder.add_node("refused", output_node)
    
    builder.add_edge(START, "input_guardrail")
    builder.add_edge("input_guardrail", "intent_router")
    builder.add_conditional_edges("intent_router", route_by_intent, {
        "rag": "rag", 
        "loan_status": "loan_status",
        "refused": "refused"
    })
    builder.add_edge("rag", "output")
    builder.add_edge("loan_status", "output")
    builder.add_edge("refused", "output")
    builder.add_edge("output", END)
    return builder

def compile_graph(checkpointer=None):
    builder = build_graph()
    if checkpointer:
        return builder.compile(checkpointer=checkpointer)
    return builder.compile()

def run_agent(query: str, thread_id: str = None, checkpointer=None) -> dict:
    graph = compile_graph(checkpointer)
    
    memory = ConversationMemory()
    history = []
    if thread_id:
        history = memory.load(thread_id)
        
    initial_state = {
        "query": query,
        "conversation_history": history
    }
    if thread_id:
        initial_state["thread_id"] = thread_id
        
    config = {"configurable": {"thread_id": thread_id}} if thread_id else None
    
    result = graph.invoke(initial_state, config=config)
    
    if thread_id:
        memory.append(thread_id, "user", query)
        memory.append(thread_id, "assistant", result.get("answer", ""))
        
    return result
