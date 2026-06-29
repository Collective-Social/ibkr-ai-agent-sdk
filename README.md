# IBKR AI Agent SDK & MCP Server

A lightweight, secure, local SDK and Model Context Protocol (MCP) server for integrating Interactive Brokers (IBKR) with AI agents like Claude and Gemini. 

## Overview
This tool allows AI Agents to act as your portfolio manager via chat. It features:
- **Local-Only Execution:** Runs alongside your TWS/IB Gateway. Credentials never leave your machine.
- **Server-Side Guardrails:** Protects your account from AI hallucinations using configurable daily drawdown limits and maximum order values.
- **MCP Integration:** Easily plug-and-play with any MCP-compatible AI client.

## Setup
1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Make sure IBKR TWS or IB Gateway is running locally on port 7496 (or 4001).
4. Run the server: `python -m mcp_server.server`

## Configuration
Edit `config.json` in the root directory to adjust guardrails:
```json
{
    "max_order_value_usd": 5000,
    "max_daily_drawdown_pct": -4.0,
    "allowed_symbols": ["AAPL", "MSFT", "GOOG", "VOO", "SPY"]
}
```
