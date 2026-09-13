import os
from pathlib import Path
from src.agent.graph import run_agent
from src.agent.memory import ConversationMemory
from src.agent.schemas import build_response

def run_demo():
    # Setup
    eval_dir = Path("evaluation/transcripts")
    eval_dir.mkdir(parents=True, exist_ok=True)
    transcript_file = eval_dir / "memory_demo.txt"
    
    memory = ConversationMemory()
    
    # Clean previous demo memory
    memory.clear("conv-demo-001")
    memory.clear("conv-demo-002")

    with open(transcript_file, "w", encoding="utf-8") as f:
        # Conversation A
        thread_a = "conv-demo-001"
        f.write(f"=== Conversation A (Thread: {thread_a}) ===\n")
        
        q1 = "What are the eligibility criteria for a home loan?"
        f.write(f"User: {q1}\n")
        memory.append(thread_a, "user", q1)
        res1 = run_agent(q1, thread_id=thread_a)
        agent_res1 = build_response(res1, q1, thread_id=thread_a)
        f.write(f"Agent: {agent_res1.answer}\n\n")
        memory.append(thread_a, "assistant", agent_res1.answer)
        
        q2 = "What about the interest rates for that?"
        f.write(f"User: {q2}\n")
        memory.append(thread_a, "user", q2)
        res2 = run_agent(q2, thread_id=thread_a)
        agent_res2 = build_response(res2, q2, thread_id=thread_a)
        f.write(f"Agent: {agent_res2.answer}\n\n")
        memory.append(thread_a, "assistant", agent_res2.answer)
        
        # Conversation B
        thread_b = "conv-demo-002"
        f.write(f"=== Conversation B (Thread: {thread_b}) ===\n")
        
        q3 = "Check status of LOAN-0001"
        f.write(f"User: {q3}\n")
        memory.append(thread_b, "user", q3)
        res3 = run_agent(q3, thread_id=thread_b)
        agent_res3 = build_response(res3, q3, thread_id=thread_b)
        f.write(f"Agent: {agent_res3.answer}\n\n")
        memory.append(thread_b, "assistant", agent_res3.answer)
        
        # Verify isolation
        f.write(f"=== Verification ===\n")
        hist_a = memory.load(thread_a)
        hist_b = memory.load(thread_b)
        
        f.write(f"Thread A history length: {len(hist_a)}\n")
        for entry in hist_a:
            f.write(f"  {entry['role']}: {entry['content']}\n")
            
        f.write(f"\nThread B history length: {len(hist_b)}\n")
        for entry in hist_b:
            f.write(f"  {entry['role']}: {entry['content']}\n")

    print(f"Memory demo transcript saved to {transcript_file}")

if __name__ == "__main__":
    run_demo()
