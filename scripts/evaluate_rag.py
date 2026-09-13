import os
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.rag.evaluation import calibrate_threshold, evaluate_chunking, run_triad_evaluation

def main():
    in_scope_queries = [
        "What are the eligibility criteria for a home loan?",
        "How is EMI calculated?",
        "What documents are needed for KYC?",
        "What is the prepayment penalty for a personal loan?",
        "What factors affect my credit score?",
        "What are the interest rates for education loans?",
        "How do I report fraud on my account?"
    ]
    
    out_of_scope_queries = [
        "What is the weather today?",
        "Tell me about quantum physics"
    ]
    
    eval_queries = [
        {"query": "What are the eligibility criteria for a home loan?", "relevant_docs": ["loan_eligibility"]},
        {"query": "How is EMI calculated?", "relevant_docs": ["emi_rules"]},
        {"query": "What documents are needed for KYC?", "relevant_docs": ["kyc_requirements"]},
        {"query": "What is the prepayment penalty for a personal loan?", "relevant_docs": ["prepayment_penalty"]},
        {"query": "What factors affect my credit score?", "relevant_docs": ["credit_score"]},
        {"query": "What are the interest rates for education loans?", "relevant_docs": ["interest_rates"]},
        {"query": "How do I report fraud on my account?", "relevant_docs": ["fraud_dispute"]},
    ]
    
    # Use absolute path based on project root to avoid issues when running from different dirs
    project_root = Path(__file__).parent.parent
    eval_dir = project_root / "evaluation"
    eval_dir.mkdir(exist_ok=True)
    
    print("Running Calibration...")
    calib = calibrate_threshold(in_scope_queries, out_of_scope_queries, "kb_fixed_chunks")
    print(f"Min in-scope: {calib['min_in_scope']:.4f}")
    print(f"Max out-of-scope: {calib['max_out_of_scope']:.4f}")
    print(f"Selected threshold: {calib['selected_threshold']:.4f}")
    
    with open(eval_dir / "rag_results.json", "w") as f:
        json.dump(calib, f, indent=4)
        
    print("\nEvaluating fixed chunks...")
    fixed_eval = evaluate_chunking(eval_queries, "kb_fixed_chunks")
    print(f"Fixed - Mean P@3: {fixed_eval['mean_precision']:.4f}, Mean R@3: {fixed_eval['mean_recall']:.4f}")
    
    print("\nEvaluating sentence chunks...")
    sent_eval = evaluate_chunking(eval_queries, "kb_sentence_chunks")
    print(f"Sentence - Mean P@3: {sent_eval['mean_precision']:.4f}, Mean R@3: {sent_eval['mean_recall']:.4f}")
    
    with open(eval_dir / "chunking_comparison.json", "w") as f:
        json.dump({
            "fixed_chunks": fixed_eval,
            "sentence_chunks": sent_eval
        }, f, indent=4)
        
    with open(eval_dir / "rag_queries.json", "w") as f:
        json.dump({
            "in_scope": in_scope_queries,
            "out_of_scope": out_of_scope_queries,
            "eval_queries": eval_queries
        }, f, indent=4)
        
    print("\nRecommendation:")
    if fixed_eval['mean_recall'] >= sent_eval['mean_recall'] and fixed_eval['mean_precision'] >= sent_eval['mean_precision']:
        print("Deploy fixed chunks strategy. It has equal or better precision and recall.")
    elif sent_eval['mean_recall'] >= fixed_eval['mean_recall'] and sent_eval['mean_precision'] >= fixed_eval['mean_precision']:
        print("Deploy sentence chunks strategy. It has equal or better precision and recall.")
    else:
        print("Deploy fixed chunks strategy as a default fallback, though metrics are mixed.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--triad":
        print("Running Triad Evaluation...")
        triad_queries = [
            {"query": "What are the eligibility criteria for a personal loan?", "topic": "loan_eligibility"},
            {"query": "How is EMI calculated for home loans?", "topic": "emi_rules"},
            {"query": "What are the annual fees for credit cards?", "topic": "credit_card_fees"},
            {"query": "What documents are required for KYC verification?", "topic": "kyc_requirements"},
            {"query": "How do I dispute a fraudulent transaction?", "topic": "fraud_dispute"},
            {"query": "What is the process to close my bank account?", "topic": "account_closure"},
            {"query": "What are the interest rates for business loans?", "topic": "interest_rates"},
            {"query": "Is there a prepayment penalty on education loans?", "topic": "prepayment_penalty"},
            {"query": "What is the minimum balance requirement for savings accounts?", "topic": "minimum_balance"},
            {"query": "What factors affect my credit score?", "topic": "credit_score"},
            {"query": "Can I open a joint account with my spouse?", "topic": "joint_accounts"},
            {"query": "What types of NRI accounts are available?", "topic": "nri_accounts"},
            {"query": "What is the meaning of life?", "topic": "out_of_scope"},
            {"query": "Tell me about cryptocurrency regulations", "topic": "out_of_scope"},
            {"query": "What are the charges?", "topic": "ambiguous"},
        ]
        
        results = run_triad_evaluation(triad_queries, "kb_fixed_chunks")
        
        print(f"{'Topic':<20} | {'Context Relevance':<18} | {'Groundedness':<12} | {'Answer Relevance'}")
        print("-" * 75)
        for res in results["query_results"]:
            print(f"{res['topic']:<20} | {res['context_relevance']:<18.4f} | {res['groundedness']:<12.4f} | {res['answer_relevance']:.4f}")
            
        print("\n--- Aggregate Scores ---")
        print(f"Mean Context Relevance: {results['mean_context_relevance']:.4f}")
        print(f"Mean Groundedness:      {results['mean_groundedness']:.4f}")
        print(f"Mean Answer Relevance:  {results['mean_answer_relevance']:.4f}")
        
        project_root = Path(__file__).parent.parent
        eval_dir = project_root / "evaluation"
        eval_dir.mkdir(exist_ok=True)
        
        with open(eval_dir / "triad_results.json", "w") as f:
            json.dump(results, f, indent=4)
            
    else:
        main()
