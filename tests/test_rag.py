import os
import pytest
import shutil
import tempfile
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.config import KB_DIR, MOCK_LLM
from src.rag.loader import load_documents
from src.rag.chunking import fixed_size_chunks, sentence_chunks
from src.rag.embeddings import embed_texts
from src.rag.indexing import build_index
from src.rag.retrieval import retrieve
from src.rag.generation import generate_answer
from src.rag.evaluation import calibrate_threshold, evaluate_chunking

@pytest.fixture(scope="session")
def test_persist_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(scope="session")
def test_docs():
    return load_documents(KB_DIR)

def test_loader_reads_all_docs(test_docs):
    assert len(test_docs) >= 1, "Should load at least 1 document"

def test_fixed_chunks_have_parent_ids(test_docs):
    chunks = fixed_size_chunks(test_docs)
    for c in chunks:
        assert "parent_doc_id" in c
        assert c["parent_doc_id"]

def test_sentence_chunks_have_parent_ids(test_docs):
    chunks = sentence_chunks(test_docs)
    for c in chunks:
        assert "parent_doc_id" in c
        assert c["parent_doc_id"]

def test_embedding_dimension():
    embeddings = embed_texts(["Test sentence"])
    assert len(embeddings) == 1
    # Check if dimension is 384 for all-MiniLM-L6-v2
    assert len(embeddings[0]) == 384

@pytest.fixture(scope="session", autouse=True)
def setup_test_index(test_persist_dir, test_docs):
    if not test_docs:
        return
    fixed_chunks = fixed_size_chunks(test_docs)
    build_index(fixed_chunks, "test_kb", persist_dir=test_persist_dir)

def test_retrieval_returns_results(test_persist_dir):
    results = retrieve("loan eligibility", collection_name="test_kb", top_k=3, persist_dir=test_persist_dir)
    assert len(results) > 0

def test_retrieval_has_parent_doc_ids(test_persist_dir):
    results = retrieve("loan", collection_name="test_kb", top_k=3, persist_dir=test_persist_dir)
    for r in results:
        assert "parent_doc_id" in r
        assert r["parent_doc_id"]

def test_mock_llm_in_scope_answer(test_persist_dir):
    results = retrieve("loan", collection_name="test_kb", top_k=3, persist_dir=test_persist_dir)
    ans = generate_answer("loan", results, threshold=0.0)
    assert ans["grounded"] is True
    assert "I don't know" not in ans["answer"]

def test_mock_llm_out_of_scope_fallback(test_persist_dir):
    results = retrieve("pizza", collection_name="test_kb", top_k=3, persist_dir=test_persist_dir)
    ans = generate_answer("pizza", results, threshold=1.0)
    assert ans["grounded"] is False
    assert "I don't know" in ans["answer"]

def test_calibration_threshold_computed(test_persist_dir):
    in_scope = ["loan"]
    out_scope = ["pizza"]
    calib = calibrate_threshold(in_scope, out_scope, collection_name="test_kb", persist_dir=test_persist_dir)
    assert isinstance(calib["selected_threshold"], float)

def test_precision_recall_computed(test_persist_dir):
    eval_queries = [
        {"query": "What are the eligibility criteria for a home loan?", "relevant_docs": ["loan_eligibility"]},
    ]
    eval_res = evaluate_chunking(eval_queries, collection_name="test_kb", top_k=3, persist_dir=test_persist_dir)
    assert isinstance(eval_res["mean_precision"], float)
    assert isinstance(eval_res["mean_recall"], float)
    assert 0.0 <= eval_res["mean_precision"] <= 1.0
    assert 0.0 <= eval_res["mean_recall"] <= 1.0

from src.rag.evaluation import context_relevance, groundedness_score, answer_relevance, run_triad_evaluation

def test_context_relevance_in_range():
    score = context_relevance("test query", ["test context chunk"])
    assert 0.0 <= score <= 1.0

def test_groundedness_score_in_range():
    score = groundedness_score("test answer", ["test context chunk"])
    assert 0.0 <= score <= 1.0

def test_answer_relevance_in_range():
    score = answer_relevance("test query", "test answer")
    assert 0.0 <= score <= 1.0

def test_triad_fallback_grounded():
    score = groundedness_score("I don't know based on the available knowledge base.", ["some context"])
    assert score == 1.0

def test_triad_results_15_queries(test_persist_dir):
    triad_queries = [
        {"query": f"test {i}", "topic": "test"} for i in range(15)
    ]
    res = run_triad_evaluation(triad_queries, collection_name="test_kb", persist_dir=test_persist_dir)
    assert len(res["query_results"]) == 15
