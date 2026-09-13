from fastmcp import FastMCP
from src.tools.loan_status import check_loan_application_status
from src.config import MCP_HOST, MCP_PORT

mcp = FastMCP("cred-loan-agent")

@mcp.tool()
def check_loan_status(record_id: str) -> dict:
    """Check the status of a loan application by record ID.
    
    Args:
        record_id: The loan application ID (e.g., 'LOAN-0001')
    
    Returns:
        Dictionary containing loan status, category, amount, escalation score and flag.
    """
    return check_loan_application_status(record_id)

if __name__ == "__main__":
    mcp.run(transport="sse", host=MCP_HOST, port=MCP_PORT)
