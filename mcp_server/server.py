import logging
from mcp.server.fastmcp import FastMCP
from ibkr_sdk.client import IBKRClient

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP Server
mcp = FastMCP("IBKR AI Agent MCP Server")

# Initialize SDK Client
# In a real environment, this might be initialized lazily or per-request
ibkr_client = IBKRClient()

@mcp.tool()
def get_account_summary() -> str:
    """
    Fetch the IBKR account summary (Net Liquidation, Cash, Margin).
    """
    if not ibkr_client.connect():
        return "Failed to connect to IBKR. Ensure TWS or Gateway is running."
    
    summary = ibkr_client.get_account_summary()
    return str(summary)

@mcp.tool()
def get_portfolio() -> str:
    """
    Fetch all active portfolio positions and their PnL.
    """
    if not ibkr_client.connect():
        return "Failed to connect to IBKR. Ensure TWS or Gateway is running."
    
    portfolio = ibkr_client.get_portfolio()
    return str(portfolio)

@mcp.tool()
def place_order(symbol: str, action: str, quantity: int, order_type: str = "MKT", price: float = 0.0) -> str:
    """
    Place a trade order on IBKR.
    :param symbol: Ticker symbol (e.g. AAPL)
    :param action: BUY or SELL
    :param quantity: Number of shares
    :param order_type: MKT or LMT
    :param price: Required if LMT
    """
    if not ibkr_client.connect():
        return "Failed to connect to IBKR. Ensure TWS or Gateway is running."
    
    result = ibkr_client.place_order(symbol, action, quantity, order_type, price)
    return str(result)

if __name__ == "__main__":
    logger.info("Starting IBKR MCP Server...")
    mcp.run()
