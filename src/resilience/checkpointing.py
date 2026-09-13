import os
from langgraph.checkpoint.sqlite import SqliteSaver
from src.config import CHECKPOINT_DB_PATH
import sqlite3

def get_checkpointer(db_path: str = None) -> SqliteSaver:
    """Create or open a SQLite checkpoint saver."""
    path = db_path or CHECKPOINT_DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    return SqliteSaver(conn)
