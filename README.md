# Cred Banking & FinTech — Production-Minded Loan Support Agent

A production-minded domain support agent for a fictional banking/lending support scenario built using LangGraph, FastAPI, and ChromaDB.

**IMPORTANT DISCLAIMER:** This entire repository is configured to run under `MOCK_LLM` logic. **Zero API keys are required to run this project.** It executes 100% locally using offline rule-based generation and local open-source embedding models (`all-MiniLM-L6-v2`).

## Included Transcripts

Transcripts demonstrating every task (Dataset generation, Indexing, RAG evaluation, Triad Self-Evaluation, LangGraph Memory Execution, and Full Test Suite Execution) are saved in the `evaluation/transcripts/` folder to prove completion.

## Acceptance Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Repository structure | ✅ Phase 1 |
| 2 | Dataset (>=40 records, all categories/statuses) | ✅ Phase 2 |
| 3 | Knowledge base (12 documents) | ✅ Phase 3 |
| 4 | Two chunking strategies + ChromaDB | ✅ Phase 4 |
| 5 | Retrieval + MOCK_LLM generation | ✅ Phase 5 |
| 6 | Similarity calibration + chunking evaluation | ✅ Phase 6 |
| 7 | Loan status tool + escalation score | ✅ Phase 7 |
| 8 | LangGraph routing (>=4 nodes, conditional edge) | ✅ Phase 8 |
| 9 | Persisted memory + structured output | ✅ Phase 9 |
| 10 | PII + injection + groundedness guardrails | ✅ Phase 10 |
| 11 | FastAPI + JSONL logging | ✅ Phase 11 |
| 12 | 15-query RAG triad evaluation | ✅ Phase 12 |
| 13 | MCP server/client | ✅ Phase 13 |
| 14 | SQLite checkpointing | ✅ Phase 14 |
| 15 | Retries + timeouts | ✅ Phase 15 |
| 16 | Full integration testing | ✅ Phase 16 |
| 17 | README complete + final audit | ✅ Phase 17 |

## Testing

```bash
# Run all tests (requires PYTHONPATH="." on Windows)
$env:PYTHONPATH="."; pytest tests/ -v
```

## Demo Commands

| # | Demo | Command |
|---|------|---------|
| 1 | Dataset generation | `python dataset.py` |
| 2 | Knowledge-base indexing | `python scripts/build_index.py` |
| 3 | RAG Evaluation | `python scripts/evaluate_rag.py` |
| 4 | Agent & Memory Demo | `python scripts/evaluate_agent.py` |
| 5 | Triad Evaluation | `python scripts/evaluate_rag.py --triad` |
| 6 | Run all demos | `python scripts/run_all_demos.py` |

## Design Details

- **Dataset**: `dataset.py` generates deterministic mocked loan application data with categories and statuses.
- **RAG Pipeline**: Loads `.md` files, chunks them using fixed and sentence strategies, embeds with `all-MiniLM-L6-v2`, stores in ChromaDB. Evaluates P@3 and R@3.
- **LangGraph**: Routes queries between `loan_status` (tools) and `rag` (retrieval) intent using a keyword regex classifier.
- **Guardrails**: PII masking (PAN, Aadhaar, Acct), injection detection, groundedness validation via word-overlap.
- **Resilience**: `checkpointing.py` for Sqlite LangGraph checkpoints, `retry.py` for exponential backoff, `timeouts.py` for Node/Global timeouts.
- **MCP**: FastMCP-powered Loan Status server and client.
