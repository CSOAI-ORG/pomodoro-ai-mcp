#!/usr/bin/env python3
"""MEOK AI Labs — pomodoro-ai-mcp MCP Server. Manage Pomodoro sessions and productivity analytics."""

import asyncio
import json
from datetime import datetime
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
)
import mcp.types as types

# In-memory store (replace with DB in production)
_store = {}

server = Server("pomodoro-ai-mcp")

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    return []

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(name="start_pomodoro", description="Start a Pomodoro session", inputSchema={"type":"object","properties":{"duration":{"type":"number"}},"required":[]}),
        Tool(name="get_stats", description="Get Pomodoro stats", inputSchema={"type":"object","properties":{}}),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Any | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    args = arguments or {}
    if name == "start_pomodoro":
        _store.setdefault("sessions", []).append(args.get("duration", 25))
        return [TextContent(type="text", text=json.dumps({"status": "started", "duration": args.get("duration", 25)}, indent=2))]
    if name == "get_stats":
        total = sum(_store.get("sessions", []))
        return [TextContent(type="text", text=json.dumps({"total_minutes": total, "sessions": len(_store.get("sessions", []))}, indent=2))]
    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}, indent=2))]

async def main():
    async with stdio_server(server._read_stream, server._write_stream) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pomodoro-ai-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
