# Cred Banking & FinTech — Production-Minded Loan Support Agent

A production-minded domain support agent for a fictional banking/lending support scenario built using LangGraph, FastAPI, and ChromaDB.

**IMPORTANT DISCLAIMER:** This entire repository is configured to run under `MOCK_LLM` logic. **Zero API keys are required to run this project.** It executes 100% locally using offline rule-based generation and local open-source embedding models (`all-MiniLM-L6-v2`).

## Included Transcripts

Transcripts demonstrating every task (Dataset generation, Indexing, RAG evaluation, Triad Self-Evaluation, LangGraph Memory Execution, and Full Test Suite Execution) are saved in the `evaluation/transcripts/` folder to prove completion.

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
