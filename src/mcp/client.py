import asyncio
import json
import sys
import os
from pathlib import Path

# Add project root to PYTHONPATH for standalone execution
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastmcp.client import Client
from src.mcp.server import mcp

TRANSCRIPT_PATH = Path(project_root) / "evaluation" / "transcripts" / "mcp_demo.txt"

async def run_client():
    TRANSCRIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    records = ["LOAN-0001", "LOAN-0005"]
    output = []
    
    print("Starting MCP Client...")
    output.append("Starting MCP Client...")
    
    # Connecting to the fastmcp instance directly
    async with Client(mcp) as client:
        for record_id in records:
            msg = f"\nCalling tool check_loan_status for record: {record_id}"
            print(msg)
            output.append(msg)
            
            try:
                res = await client.call_tool("check_loan_status", {"record_id": record_id})
                # Format response beautifully
                response_data = res.structured_content if res.structured_content else res.content[0].text
                msg2 = f"Response: {json.dumps(response_data, indent=2)}"
                print(msg2)
                output.append(msg2)
            except Exception as e:
                msg_err = f"Error: {e}"
                print(msg_err)
                output.append(msg_err)

    print(f"\nSaving transcript to {TRANSCRIPT_PATH}")
    
    with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(output) + "\n")

if __name__ == "__main__":
    asyncio.run(run_client())
