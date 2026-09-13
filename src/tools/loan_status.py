import json
from typing import Dict, Any, Optional
from pathlib import Path
from src.config import PROJECT_ROOT

DATA_PATH = PROJECT_ROOT / "data" / "loan_applications.json"

_cached_data: Optional[Dict[str, Any]] = None

def load_loan_data(filepath: Optional[Path | str] = None) -> dict:
    global _cached_data
    use_cache = (filepath is None)
    
    if filepath is None:
        filepath = DATA_PATH
    
    if use_cache and _cached_data is not None:
        return _cached_data
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            records = json.load(f)
        
        data_dict = {r["record_id"]: r for r in records}
        if use_cache:
            _cached_data = data_dict
        return data_dict
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def check_loan_application_status(record_id: str) -> dict:
    data = load_loan_data()
    if record_id not in data:
        return {"error": "Record not found", "record_id": record_id}
    
    record = data[record_id]
    
    days_since_created = record.get("days_since_created", 365)
    flagged_for_fraud_review = record.get("flagged_for_fraud_review", False)
    
    recency_score = 1.0 - (days_since_created / 365.0)
    fraud_weight = 0.6 if flagged_for_fraud_review else 0.0
    recency_weight = 0.4
    
    escalation_score = fraud_weight + recency_weight * recency_score
    escalation_score = max(0.0, min(1.0, escalation_score))
    
    escalation_flag = escalation_score >= 0.5
    
    return {
        "record_id": record["record_id"],
        "status": record["status"],
        "category": record["category"],
        "loan_amount_inr": record["loan_amount_inr"],
        "days_since_created": days_since_created,
        "flagged_for_fraud_review": flagged_for_fraud_review,
        "escalation_score": round(escalation_score, 4),
        "escalation_flag": escalation_flag
    }
