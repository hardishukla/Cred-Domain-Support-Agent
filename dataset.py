import json
import random
import os
from collections import Counter
from typing import List, Dict, Any

def generate_dataset(seed: int = 42, size: int = 50) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    
    if size < 40:
        size = 40
        
    categories = ["Personal Loan", "Home Loan", "Auto Loan", "Education Loan", "Business Loan"]
    category_weights = [30, 20, 20, 15, 15]
    
    statuses = ["Submitted", "Under Review", "Approved", "Rejected", "Disbursed"]
    status_weights = [25, 25, 20, 15, 15]
    
    records = []
    
    for i in range(1, size + 1):
        record_id = f"LOAN-{i:04d}"
        category = rng.choices(categories, weights=category_weights, k=1)[0]
        status = rng.choices(statuses, weights=status_weights, k=1)[0]
        loan_amount_inr = rng.randint(50000, 5000000)
        days_since_created = rng.randint(1, 365)
        flagged_for_fraud_review = rng.random() < 0.18
        
        records.append({
            "record_id": record_id,
            "category": category,
            "status": status,
            "loan_amount_inr": loan_amount_inr,
            "days_since_created": days_since_created,
            "flagged_for_fraud_review": flagged_for_fraud_review
        })
        
    # Constraint enforcement
    # 1. Any category < 3 records -> reassign from largest
    category_counts = Counter(r["category"] for r in records)
    for cat in categories:
        while category_counts[cat] < 3:
            largest_cat = max(category_counts, key=category_counts.get)
            # Find a record with largest_cat
            candidates = [r for r in records if r["category"] == largest_cat]
            if candidates:
                record_to_change = rng.choice(candidates)
                record_to_change["category"] = cat
                category_counts[largest_cat] -= 1
                category_counts[cat] += 1

    # 2. Any status missing -> swap from most common status
    status_counts = Counter(r["status"] for r in records)
    for stat in statuses:
        if status_counts[stat] == 0:
            largest_stat = max(status_counts, key=status_counts.get)
            candidates = [r for r in records if r["status"] == largest_stat]
            if candidates:
                record_to_change = rng.choice(candidates)
                record_to_change["status"] = stat
                status_counts[largest_stat] -= 1
                status_counts[stat] += 1
                
    # 3. Fraud-review % between 10% and 30%
    while True:
        fraud_count = sum(r["flagged_for_fraud_review"] for r in records)
        fraud_percent = (fraud_count / len(records)) * 100
        
        if fraud_percent < 10.0:
            candidates = [r for r in records if not r["flagged_for_fraud_review"]]
            if candidates:
                record_to_change = rng.choice(candidates)
                record_to_change["flagged_for_fraud_review"] = True
        elif fraud_percent > 30.0:
            candidates = [r for r in records if r["flagged_for_fraud_review"]]
            if candidates:
                record_to_change = rng.choice(candidates)
                record_to_change["flagged_for_fraud_review"] = False
        else:
            break
            
    # Validation assertions
    assert len(records) >= 40, f"Total records {len(records)} < 40"
    
    final_category_counts = Counter(r["category"] for r in records)
    for cat in categories:
        assert final_category_counts[cat] >= 3, f"Category {cat} has {final_category_counts[cat]} < 3 records"
        
    final_status_counts = Counter(r["status"] for r in records)
    for stat in statuses:
        assert final_status_counts[stat] >= 1, f"Status {stat} is missing"
        
    fraud_count = sum(r["flagged_for_fraud_review"] for r in records)
    fraud_percent = (fraud_count / len(records)) * 100
    assert 10.0 <= fraud_percent <= 30.0, f"Fraud % {fraud_percent} not between 10 and 30"
    
    return records

if __name__ == "__main__":
    records = generate_dataset()
    
    total = len(records)
    categories = Counter(r["category"] for r in records)
    statuses = Counter(r["status"] for r in records)
    fraud_count = sum(1 for r in records if r["flagged_for_fraud_review"])
    fraud_percent = (fraud_count / total) * 100
    
    print(f"Total Records: {total}")
    print("\nCounts per Category:")
    for cat, count in categories.items():
        print(f"  {cat}: {count}")
        
    print("\nCounts per Status:")
    for stat, count in statuses.items():
        print(f"  {stat}: {count}")
        
    print(f"\nFraud Count: {fraud_count}")
    print(f"Fraud Percentage: {fraud_percent:.1f}%")
    
    # Save to data/loan_applications.json
    os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
    file_path = os.path.join(os.path.dirname(__file__), "data", "loan_applications.json")
    with open(file_path, "w") as f:
        json.dump(records, f, indent=2)
        
    print("\nDataset saved to data/loan_applications.json")
