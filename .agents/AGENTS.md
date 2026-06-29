# IBKR AI Agent SDK - Agent Instructions

You are an AI coding assistant (e.g. Antigravity, Cursor, Cline, Windsurf) working on the `ibkr-ai-agent-sdk` repository.
This repository contains a Model Context Protocol (MCP) server that connects to Interactive Brokers (IBKR).

## Project Structure
- `ibkr_sdk/`: The core python SDK for connecting to the IBKR TWS API and enforcing trade guardrails.
  - `client.py`: Uses `ibapi` to interact with IBKR.
  - `guardrails.py`: Enforces critical financial safety measures (ticker whitelists, max quantities).
- `mcp_server/`: The Model Context Protocol implementation.
  - `server.py`: Uses the `mcp.server.fastmcp` module to expose `ibkr_sdk` functions to the AI agent client.
- `landing_page/`: The HTML/CSS marketing page hosted on Vercel at `ibkr-mcp.ai.collective.social`.

## Core Philosophy
- **Safety First**: Any modifications to trading logic MUST preserve or strengthen existing guardrails. Never bypass the quantity limits or ticker whitelists without explicit user consent.
- **MCP Standards**: Ensure `mcp_server/server.py` follows the official Model Context Protocol specification for exposing tools.

## Testing & Verification
When the user asks you to test changes to the trading logic or MCP server:
1. Advise the user to ensure Interactive Brokers TWS or IB Gateway is running and logged into a **Paper Trading** account.
2. The default port is `7497`.
3. You can test the MCP server by running `python mcp_server/server.py` directly, or using the MCP Inspector tool.
