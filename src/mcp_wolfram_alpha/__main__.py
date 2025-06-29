#!/usr/bin/env python3
"""
Entry point for running the MCP Wolfram Alpha server as a module.
This allows the server to be started with: python -m mcp_wolfram_alpha
"""

import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())
