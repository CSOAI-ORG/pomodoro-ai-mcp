# Pomodoro Ai

> By [MEOK AI Labs](https://meok.ai) — Manage Pomodoro focus sessions, breaks, and productivity analytics. By MEOK AI Labs.

Pomodoro AI — manage focus sessions, breaks, and productivity analytics. MEOK AI Labs.

## Installation

```bash
pip install pomodoro-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install pomodoro-ai-mcp
```

## Tools

### `start_session`
Start a new Pomodoro focus session. Optionally specify a task name and custom duration (default uses configured timer).

**Parameters:**
- `task` (str)
- `duration_minutes` (int)

### `stop_session`
Stop the current Pomodoro session. Mark as completed or interrupted. Add optional notes.

**Parameters:**
- `completed` (bool)
- `notes` (str)

### `get_stats`
Get Pomodoro productivity statistics for the last N days (default 7).

**Parameters:**
- `days` (int)

### `configure_timer`
Configure Pomodoro timer durations. Customise work, short break, long break, and session count before long break.

**Parameters:**
- `work_minutes` (int)
- `short_break` (int)
- `long_break` (int)
- `sessions_before_long` (int)

### `get_productivity_report`
Generate a detailed productivity report with insights and recommendations.


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/pomodoro-ai-mcp](https://github.com/CSOAI-ORG/pomodoro-ai-mcp)
- **PyPI**: [pypi.org/project/pomodoro-ai-mcp](https://pypi.org/project/pomodoro-ai-mcp/)

## License

MIT — MEOK AI Labs
