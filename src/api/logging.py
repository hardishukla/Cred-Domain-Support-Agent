import json
import logging
from datetime import datetime
from src.config import PROJECT_ROOT

log_dir = PROJECT_ROOT / "logs"
log_dir.mkdir(exist_ok=True)
jsonl_file = log_dir / "api_requests.jsonl"

def log_request_response(trace_id: str, request_data: dict, response_data: dict, endpoint: str):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "trace_id": trace_id,
        "endpoint": endpoint,
        "request": request_data,
        "response": response_data
    }
    with open(jsonl_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
