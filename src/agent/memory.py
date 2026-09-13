import json
import os
from pathlib import Path
from src.config import MEMORY_DIR

class ConversationMemory:
    def __init__(self, memory_dir: str = None):
        self.memory_dir = Path(memory_dir or MEMORY_DIR)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
    
    def _filepath(self, thread_id: str) -> Path:
        return self.memory_dir / f"{thread_id}.json"
    
    def load(self, thread_id: str) -> list[dict]:
        """Load conversation history for a thread."""
        fp = self._filepath(thread_id)
        if fp.exists():
            with open(fp, 'r') as f:
                return json.load(f)
        return []
    
    def save(self, thread_id: str, history: list[dict]) -> None:
        """Save conversation history for a thread."""
        with open(self._filepath(thread_id), 'w') as f:
            json.dump(history, f, indent=2)
    
    def append(self, thread_id: str, role: str, content: str) -> None:
        """Append a turn to conversation history."""
        history = self.load(thread_id)
        history.append({"role": role, "content": content})
        self.save(thread_id, history)
    
    def clear(self, thread_id: str) -> None:
        """Clear conversation history for a thread."""
        fp = self._filepath(thread_id)
        if fp.exists():
            fp.unlink()
