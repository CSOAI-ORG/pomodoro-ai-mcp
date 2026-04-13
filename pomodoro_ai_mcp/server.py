import time
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pomodoro")

DEFAULT_WORK = 25 * 60
DEFAULT_BREAK = 5 * 60

STATE = {
    "active": False,
    "mode": "work",
    "start_time": None,
    "duration": DEFAULT_WORK,
    "completed_work": 0,
    "completed_breaks": 0,
}

@mcp.tool()
def start_pomodoro(work_minutes: int = 25, break_minutes: int = 5) -> dict:
    """Start a Pomodoro session."""
    STATE["active"] = True
    STATE["mode"] = "work"
    STATE["start_time"] = time.time()
    STATE["duration"] = work_minutes * 60
    return {"status": "work_started", "duration_seconds": STATE["duration"]}

@mcp.tool()
def check_status() -> dict:
    """Check active session status."""
    if not STATE["active"] or STATE["start_time"] is None:
        return {"active": False, "completed_work": STATE["completed_work"], "completed_breaks": STATE["completed_breaks"]}
    elapsed = time.time() - STATE["start_time"]
    remaining = max(0, STATE["duration"] - elapsed)
    finished = remaining <= 0
    if finished:
        if STATE["mode"] == "work":
            STATE["completed_work"] += 1
        else:
            STATE["completed_breaks"] += 1
        STATE["active"] = False
    return {
        "active": STATE["active"],
        "mode": STATE["mode"],
        "remaining_seconds": round(remaining, 1),
        "finished": finished,
        "completed_work": STATE["completed_work"],
        "completed_breaks": STATE["completed_breaks"],
    }

@mcp.tool()
def get_stats() -> dict:
    """Get Pomodoro statistics."""
    return {
        "completed_work_sessions": STATE["completed_work"],
        "completed_break_sessions": STATE["completed_breaks"],
        "total_focus_minutes": STATE["completed_work"] * 25,
    }

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
