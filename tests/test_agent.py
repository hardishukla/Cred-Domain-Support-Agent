import pytest
import os
from src.agent.router import classify_intent, extract_record_id
from src.agent.graph import build_graph, run_agent

def test_intent_classifier_rag():
    assert classify_intent("What is the EMI formula?") == "rag"

def test_intent_classifier_status():
    assert classify_intent("Check status of LOAN-0005") == "loan_status"

def test_intent_classifier_status_keyword():
    assert classify_intent("What is my application status?") == "loan_status"

def test_extract_record_id():
    assert extract_record_id("Check LOAN-0005") == "LOAN-0005"

def test_extract_record_id_none():
    assert extract_record_id("What is EMI?") is None

def test_graph_has_min_5_nodes():
    graph = build_graph()
    assert len(graph.nodes) >= 5

def test_rag_route_full():
    result = run_agent("What are the eligibility criteria for a home loan?")
    assert result.get("answer") is not None
    assert result.get("answer") != "No answer generated."
    assert result.get("route") == "rag"

def test_loan_status_route_full():
    result = run_agent("Check status of LOAN-0001")
    assert result.get("answer") is not None
    assert "LOAN-0001" in result.get("answer")
    assert result.get("route") == "loan_status"
    assert "escalation_score" in result

def test_out_of_scope_query():
    result = run_agent("What is quantum physics?")
    assert "I don't know" in result.get("answer")

from src.agent.memory import ConversationMemory
from src.agent.schemas import AgentResponse, build_response
from pydantic import ValidationError

def test_memory_save_and_load(tmpdir):
    mem = ConversationMemory(memory_dir=str(tmpdir))
    thread_id = "test-thread-1"
    history = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
    mem.save(thread_id, history)
    loaded = mem.load(thread_id)
    assert loaded == history

def test_memory_thread_isolation(tmpdir):
    mem = ConversationMemory(memory_dir=str(tmpdir))
    mem.save("thread-A", [{"role": "user", "content": "hi"}])
    loaded = mem.load("thread-B")
    assert loaded == []

def test_memory_append(tmpdir):
    mem = ConversationMemory(memory_dir=str(tmpdir))
    thread_id = "test-thread-append"
    mem.append(thread_id, "user", "q1")
    mem.append(thread_id, "assistant", "a1")
    loaded = mem.load(thread_id)
    assert len(loaded) == 2
    assert loaded[0]["content"] == "q1"
    assert loaded[1]["content"] == "a1"

def test_schema_valid_response():
    resp = AgentResponse(query="test", answer="answer", route="rag")
    assert resp.query == "test"
    assert resp.answer == "answer"
    assert resp.trace_id is not None

def test_schema_rejects_missing_required():
    with pytest.raises(ValidationError):
        AgentResponse(query="missing answer", route="rag")

def test_build_response_from_state():
    state = {
        "answer": "my answer",
        "route": "loan_status",
        "grounded": True,
        "sources": ["db"],
        "escalation_score": 0.5,
        "escalation_flag": False,
        "error": None
    }
    resp = build_response(state, query="q", thread_id="t1")
    assert resp.query == "q"
    assert resp.answer == "my answer"
    assert resp.route == "loan_status"
    assert resp.thread_id == "t1"

