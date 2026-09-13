import pytest
from dataset import generate_dataset
from collections import Counter

def test_record_count():
    records = generate_dataset(size=50)
    assert len(records) >= 40
    records2 = generate_dataset(size=30)
    assert len(records2) >= 40

def test_all_categories_present():
    records = generate_dataset()
    categories = {r["category"] for r in records}
    expected_categories = {"Personal Loan", "Home Loan", "Auto Loan", "Education Loan", "Business Loan"}
    assert categories == expected_categories

def test_min_3_per_category():
    records = generate_dataset()
    counts = Counter(r["category"] for r in records)
    for cat, count in counts.items():
        assert count >= 3

def test_all_statuses_present():
    records = generate_dataset()
    statuses = {r["status"] for r in records}
    expected_statuses = {"Submitted", "Under Review", "Approved", "Rejected", "Disbursed"}
    assert statuses == expected_statuses

def test_fraud_percentage_range():
    records = generate_dataset()
    fraud_count = sum(1 for r in records if r["flagged_for_fraud_review"])
    percent = (fraud_count / len(records)) * 100
    assert 10.0 <= percent <= 30.0

def test_deterministic_seed():
    records1 = generate_dataset(seed=42)
    records2 = generate_dataset(seed=42)
    assert records1 == records2
    
    records3 = generate_dataset(seed=99)
    # Most likely they will be different
    assert records1 != records3

def test_record_schema():
    records = generate_dataset()
    for r in records:
        assert isinstance(r["record_id"], str)
        assert r["record_id"].startswith("LOAN-")
        assert isinstance(r["category"], str)
        assert isinstance(r["status"], str)
        assert isinstance(r["loan_amount_inr"], int)
        assert isinstance(r["days_since_created"], int)
        assert isinstance(r["flagged_for_fraud_review"], bool)

def test_loan_amount_range():
    records = generate_dataset()
    for r in records:
        assert 50000 <= r["loan_amount_inr"] <= 5000000

def test_days_since_created_range():
    records = generate_dataset()
    for r in records:
        assert 1 <= r["days_since_created"] <= 365

from src.tools.loan_status import check_loan_application_status, load_loan_data

def test_valid_record_lookup():
    data = load_loan_data()
    if not data:
        pytest.skip('No data available')
    first_key = list(data.keys())[0]
    result = check_loan_application_status(first_key)
    assert 'error' not in result
    assert result['record_id'] == first_key
    assert 'status' in result
    assert 'escalation_score' in result

def test_invalid_record_returns_error():
    result = check_loan_application_status('NONEXISTENT')
    assert 'error' in result
    assert result['record_id'] == 'NONEXISTENT'

def test_escalation_score_range():
    data = load_loan_data()
    for rid in data:
        result = check_loan_application_status(rid)
        assert 0.0 <= result['escalation_score'] <= 1.0

def test_fraud_flagged_always_escalated():
    data = load_loan_data()
    for rid, record in data.items():
        if record.get('flagged_for_fraud_review'):
            result = check_loan_application_status(rid)
            assert result['escalation_score'] >= 0.5
            assert result['escalation_flag'] is True

def test_escalation_formula_deterministic():
    data = load_loan_data()
    if data:
        first_key = list(data.keys())[0]
        res1 = check_loan_application_status(first_key)
        res2 = check_loan_application_status(first_key)
        assert res1['escalation_score'] == res2['escalation_score']

def test_escalation_flag_threshold():
    data = load_loan_data()
    for rid in data:
        result = check_loan_application_status(rid)
        if result['escalation_score'] >= 0.5:
            assert result['escalation_flag'] is True
        else:
            assert result['escalation_flag'] is False

def test_return_schema():
    data = load_loan_data()
    if data:
        first_key = list(data.keys())[0]
        result = check_loan_application_status(first_key)
        expected_keys = {
            'record_id', 'status', 'category', 'loan_amount_inr', 
            'days_since_created', 'flagged_for_fraud_review', 
            'escalation_score', 'escalation_flag'
        }
        assert set(result.keys()) == expected_keys