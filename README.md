<div align="center">

# Pomodoro Ai MCP

**MCP server for pomodoro ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-pomodoro-ai-mcp)](https://pypi.org/project/meok-pomodoro-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Pomodoro Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `start_session` | Start a new Pomodoro focus session. Optionally specify a task name and custom du |
| `stop_session` | Stop the current Pomodoro session. Mark as completed or interrupted. Add optiona |
| `get_stats` | Get Pomodoro productivity statistics for the last N days (default 7). |
| `configure_timer` | Configure Pomodoro timer durations. Customise work, short break, long break, and |
| `get_productivity_report` | Generate a detailed productivity report with insights and recommendations. |

## Installation

```bash
pip install meok-pomodoro-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "pomodoro-ai": {
      "command": "python",
      "args": ["-m", "meok_pomodoro_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 5 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
