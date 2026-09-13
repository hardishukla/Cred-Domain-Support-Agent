import pytest
import asyncio
from src.tools.loan_status import check_loan_application_status
from src.mcp.server import mcp
from fastmcp.client import Client

def test_mcp_tool_returns_valid_record():
    result = check_loan_application_status("LOAN-0001")
    assert "error" not in result
    assert result["record_id"] == "LOAN-0001"

def test_mcp_tool_returns_error_for_invalid():
    result = check_loan_application_status("NONEXISTENT")
    assert "error" in result
    assert result["error"] == "Record not found"

def test_mcp_tool_response_has_required_keys():
    result = check_loan_application_status("LOAN-0001")
    assert "record_id" in result
    assert "status" in result
    assert "escalation_score" in result

def test_mcp_server_has_tool():
    # Verify the server has the tool registered
    # mcp.list_tools() is an async function in modern fastmcp 
    pass

@pytest.mark.asyncio
async def test_mcp_client_call():
    # Use Client to call the tool and verify response
    async with Client(mcp) as client:
        res = await client.call_tool("check_loan_status", {"record_id": "LOAN-0001"})
        
        # Determine how data is structured in fastmcp response
        if res.structured_content:
            data = res.structured_content
        else:
            import json
            data = json.loads(res.content[0].text)
            
        assert data["record_id"] == "LOAN-0001"
        assert "escalation_score" in data
