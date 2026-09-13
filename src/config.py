"""
config.py — Centralised configuration for the Cred Loan Support Agent.

Reads from environment variables / .env file.
Defaults ensure the project works under MOCK_LLM with zero API keys.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env if present (not required — defaults are sufficient)
load_dotenv()

# ── Paths ────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
KB_DIR = DATA_DIR / "knowledge_base"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(PROJECT_ROOT / "chroma_db"))
CHECKPOINT_DB_PATH = os.getenv("CHECKPOINT_DB_PATH", str(PROJECT_ROOT / "checkpoints" / "checkpoints.sqlite"))
MEMORY_DIR = os.getenv("MEMORY_DIR", str(DATA_DIR / "memory"))
LOG_FILE = os.getenv("LOG_FILE", str(PROJECT_ROOT / "logs" / "requests.jsonl"))

# ── LLM mode ────────────────────────────────────────────────
MOCK_LLM: bool = os.getenv("MOCK_LLM", "true").lower() == "true"

# ── Dataset ──────────────────────────────────────────────────
DATASET_SEED: int = int(os.getenv("DATASET_SEED", "42"))
DATASET_SIZE: int = int(os.getenv("DATASET_SIZE", "50"))

# ── Embedding ────────────────────────────────────────────────
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# ── RAG ──────────────────────────────────────────────────────
RAG_SIMILARITY_THRESHOLD: float = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.35"))

# ── API ──────────────────────────────────────────────────────
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))

# ── MCP ──────────────────────────────────────────────────────
MCP_HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT: int = int(os.getenv("MCP_PORT", "8001"))

# ── Resilience ───────────────────────────────────────────────
RETRY_MAX_ATTEMPTS: int = int(os.getenv("RETRY_MAX_ATTEMPTS", "3"))
RETRY_INITIAL_INTERVAL: float = float(os.getenv("RETRY_INITIAL_INTERVAL", "1.0"))
RETRY_MAX_INTERVAL: float = float(os.getenv("RETRY_MAX_INTERVAL", "10.0"))
RETRY_JITTER: bool = os.getenv("RETRY_JITTER", "true").lower() == "true"

PER_NODE_TIMEOUT: int = int(os.getenv("PER_NODE_TIMEOUT", "30"))
GLOBAL_GRAPH_TIMEOUT: int = int(os.getenv("GLOBAL_GRAPH_TIMEOUT", "120"))
