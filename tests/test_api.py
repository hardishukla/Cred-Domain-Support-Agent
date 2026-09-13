import pytest
from fastapi.testclient import TestClient
from src.api.routes import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_chat_endpoint_rag():
    response = client.post("/chat", json={"query": "What is the EMI formula?", "thread_id": "test1"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["route"] == "rag"
    assert data["query"] == "What is the EMI formula?"
    assert data["thread_id"] == "test1"

def test_chat_endpoint_loan_status():
    response = client.post("/chat", json={"query": "Check status of LOAN-0001", "thread_id": "test2"})
    assert response.status_code == 200
    data = response.json()
    assert data["route"] == "loan_status"
    assert "escalation_score" in data

def test_chat_endpoint_missing_query():
    response = client.post("/chat", json={"thread_id": "test3"})
    assert response.status_code == 422  # validation error
