"""
Local MCP Server - Banking Tools
================================

This is a simple LOCAL MCP server that exposes banking tools.
It can be used by any MCP client, including Microsoft Agent Framework.

TWO WAYS TO BUILD MCP SERVERS:
1. FastMCP (simpler) - This file uses FastMCP
2. MCP SDK directly (more control) - See local_mcp_server_sdk.py

HOW IT WORKS:
┌─────────────────┐         STDIO          ┌─────────────────┐
│   MCP Client    │ ◄──── stdin/stdout ───► │   MCP Server    │
│ (Agent Framework)│                        │ (This file)     │
└─────────────────┘                         └─────────────────┘

SETUP:
    pip install fastmcp

RUN (for testing):
    python local_mcp_server.py

USE WITH AGENT:
    See client_local_mcp.py
"""

from fastmcp import FastMCP
from datetime import datetime
from typing import Optional

# =============================================================================
# CREATE THE MCP SERVER
# =============================================================================

mcp = FastMCP(
    name="BankingToolsServer",
    instructions="""
    This MCP server provides banking tools:
    - Check account balance
    - List transactions
    - Get payment methods
    - Calculate loan payments
    """
)

# =============================================================================
# FAKE DATA (Simulates a database)
# =============================================================================

ACCOUNTS = {
    "ACC001": {"balance": 5420.50, "type": "Checking", "owner": "John Smith"},
    "ACC002": {"balance": 12500.00, "type": "Savings", "owner": "John Smith"},
}

TRANSACTIONS = [
    {"date": "2025-02-15", "amount": -45.00, "merchant": "Starbucks", "category": "Restaurant"},
    {"date": "2025-02-14", "amount": -120.00, "merchant": "Amazon", "category": "Shopping"},
    {"date": "2025-02-13", "amount": 3500.00, "merchant": "Employer Inc", "category": "Salary"},
    {"date": "2025-02-12", "amount": -65.00, "merchant": "Shell Gas", "category": "Gas"},
    {"date": "2025-02-11", "amount": -89.99, "merchant": "Netflix", "category": "Entertainment"},
]

PAYMENT_METHODS = [
    {"type": "credit_card", "name": "Visa Gold", "last_four": "4242", "is_default": True},
    {"type": "credit_card", "name": "Mastercard", "last_four": "8888", "is_default": False},
    {"type": "bank_account", "name": "Checking", "last_four": "1234", "is_default": False},
]


# =============================================================================
# MCP TOOLS - These are exposed to MCP clients
# =============================================================================

@mcp.tool()
def get_account_balance(account_id: str = "ACC001") -> dict:
    """
    Get the current balance for a bank account.
    
    Use this when the user asks about their balance or how much money they have.
    
    Args:
        account_id: The account identifier (default: ACC001)
        
    Returns:
        Account balance information including balance, type, and owner
    """
    account = ACCOUNTS.get(account_id)
    if account:
        return {
            "account_id": account_id,
            "balance": account["balance"],
            "account_type": account["type"],
            "owner": account["owner"],
            "currency": "USD",
            "as_of": datetime.now().isoformat()
        }
    return {"error": f"Account {account_id} not found"}


@mcp.tool()
def get_recent_transactions(limit: int = 5) -> list:
    """
    Get recent transaction history.
    
    Use this when the user asks about recent spending, transactions, or activity.
    
    Args:
        limit: Maximum number of transactions to return (default: 5)
        
    Returns:
        List of recent transactions with date, amount, merchant, and category
    """
    return TRANSACTIONS[:limit]


@mcp.tool()
def search_transactions(
    category: Optional[str] = None,
    merchant: Optional[str] = None,
    min_amount: Optional[float] = None
) -> list:
    """
    Search transactions with filters.
    
    Use this when the user asks about specific spending like:
    - "How much did I spend at Starbucks?"
    - "Show me my restaurant expenses"
    - "Find transactions over $100"
    
    Args:
        category: Filter by category (e.g., "Restaurant", "Shopping")
        merchant: Filter by merchant name (partial match)
        min_amount: Minimum transaction amount (absolute value)
        
    Returns:
        List of matching transactions
    """
    results = []
    for txn in TRANSACTIONS:
        # Apply filters
        if category and txn["category"].lower() != category.lower():
            continue
        if merchant and merchant.lower() not in txn["merchant"].lower():
            continue
        if min_amount and abs(txn["amount"]) < min_amount:
            continue
        results.append(txn)
    
    return results


@mcp.tool()
def get_payment_methods() -> list:
    """
    Get all available payment methods.
    
    Use this when the user asks about their cards, payment options,
    or how they can pay for something.
    
    Returns:
        List of payment methods (credit cards, bank accounts)
    """
    return PAYMENT_METHODS


@mcp.tool()
def calculate_loan_payment(
    principal: float,
    annual_rate: float,
    years: int
) -> dict:
    """
    Calculate monthly loan payment.
    
    Use this when the user asks about loan calculations, mortgages,
    or how much their monthly payment would be.
    
    Args:
        principal: Loan amount in dollars
        annual_rate: Annual interest rate as percentage (e.g., 5.5 for 5.5%)
        years: Loan term in years
        
    Returns:
        Monthly payment, total payment, and total interest
    """
    # Convert annual rate to monthly rate
    monthly_rate = (annual_rate / 100) / 12
    num_payments = years * 12
    
    # Calculate monthly payment using formula
    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    
    total_payment = monthly_payment * num_payments
    total_interest = total_payment - principal
    
    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "principal": principal,
        "annual_rate": annual_rate,
        "term_years": years,
        "num_payments": num_payments
    }


@mcp.tool()
def get_spending_summary() -> dict:
    """
    Get a summary of spending by category.
    
    Use this when the user asks about where their money goes,
    spending breakdown, or budget analysis.
    
    Returns:
        Dictionary with spending totals by category
    """
    summary = {}
    for txn in TRANSACTIONS:
        if txn["amount"] < 0:  # Only expenses
            category = txn["category"]
            summary[category] = summary.get(category, 0) + abs(txn["amount"])
    
    # Round values
    summary = {k: round(v, 2) for k, v in summary.items()}
    
    return {
        "spending_by_category": summary,
        "total_spending": round(sum(summary.values()), 2),
        "period": "Last 30 days"
    }


# =============================================================================
# MCP RESOURCES (Read-only data)
# =============================================================================

@mcp.resource("resource://account-types")
def get_account_types() -> dict:
    """List of available account types."""
    return {
        "account_types": ["Checking", "Savings", "Money Market", "CD"],
        "description": "Available account types at our bank"
    }


@mcp.resource("resource://interest-rates")
def get_interest_rates() -> dict:
    """Current interest rates."""
    return {
        "savings_apy": 4.5,
        "checking_apy": 0.1,
        "cd_12_month_apy": 5.0,
        "mortgage_30_year": 6.75,
        "auto_loan": 7.5,
        "as_of": datetime.now().strftime("%Y-%m-%d")
    }


# =============================================================================
# MAIN - Run the server
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🏦 Banking MCP Server")
    print("=" * 60)
    print(f"Server Name: {mcp.name}")
    print("\n📋 Available Tools:")
    print("  • get_account_balance")
    print("  • get_recent_transactions")
    print("  • search_transactions")
    print("  • get_payment_methods")
    print("  • calculate_loan_payment")
    print("  • get_spending_summary")
    print("\n📚 Available Resources:")
    print("  • resource://account-types")
    print("  • resource://interest-rates")
    print("\n" + "=" * 60)
    print("Starting MCP server (STDIO mode)...")
    print("Use Ctrl+C to stop")
    print("=" * 60)
    
    # Run the server in STDIO mode
    # This is what MCPStdioTool connects to
    mcp.run()