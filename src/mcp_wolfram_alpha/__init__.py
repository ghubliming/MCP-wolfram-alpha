from . import server
from .server import (
    server as mcp_server,
    handle_list_prompts,
    handle_get_prompt, 
    handle_list_tools,
    handle_call_tool,
    main
)
import asyncio


# Optionally expose other important items at package level
__all__ = [
    "main", 
    "server", 
    "mcp_server",
    "handle_list_prompts",
    "handle_get_prompt", 
    "handle_list_tools",
    "handle_call_tool"
]
