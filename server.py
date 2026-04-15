#!/usr/bin/env python3
"""Pomodoro AI — manage focus sessions, breaks, and productivity analytics. MEOK AI Labs."""
import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

# In-memory session store
_sessions: list[dict] = []
_config = {
    "work_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 15,
    "sessions_before_long_break": 4,
}
_active_session: dict | None = None

mcp = FastMCP("pomodoro-ai", instructions="Manage Pomodoro focus sessions, breaks, and productivity analytics. By MEOK AI Labs.")


@mcp.tool()
def start_session(task: str = "Deep Work", duration_minutes: int = 0, api_key: str = "") -> str:
    """Start a new Pomodoro focus session. Optionally specify a task name and custom duration (default uses configured timer)."""
    global _active_session
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    if _active_session:
        return json.dumps({"error": "A session is already active. Stop it first.", "active_session": _active_session})
    duration = duration_minutes if duration_minutes > 0 else _config["work_minutes"]
    session_number = len(_sessions) + 1
    # Determine break type after this session
    sessions_since_long = session_number % _config["sessions_before_long_break"]
    is_long_break_next = sessions_since_long == 0
    _active_session = {
        "id": session_number,
        "task": task,
        "duration_minutes": duration,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
    }
    break_type = "long" if is_long_break_next else "short"
    break_duration = _config["long_break_minutes"] if is_long_break_next else _config["short_break_minutes"]
    return json.dumps({
        "session": _active_session,
        "message": f"Focus session #{session_number} started! {duration} minutes on '{task}'.",
        "next_break": {"type": break_type, "duration_minutes": break_duration},
        "tip": "Silence notifications and commit to single-tasking.",
    }, indent=2)


@mcp.tool()
def stop_session(completed: bool = True, notes: str = "", api_key: str = "") -> str:
    """Stop the current Pomodoro session. Mark as completed or interrupted. Add optional notes."""
    global _active_session
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    if not _active_session:
        return json.dumps({"error": "No active session to stop."})
    ended_at = datetime.now(timezone.utc)
    started_at = datetime.fromisoformat(_active_session["started_at"])
    actual_minutes = round((ended_at - started_at).total_seconds() / 60, 1)
    record = {
        **_active_session,
        "ended_at": ended_at.isoformat(),
        "actual_minutes": actual_minutes,
        "completed": completed,
        "notes": notes,
        "status": "completed" if completed else "interrupted",
    }
    _sessions.append(record)
    _active_session = None
    # Calculate today's stats
    today = datetime.now(timezone.utc).date().isoformat()
    today_sessions = [s for s in _sessions if s["started_at"][:10] == today]
    today_focus = sum(s["actual_minutes"] for s in today_sessions)
    today_completed = sum(1 for s in today_sessions if s["completed"])
    return json.dumps({
        "session": record,
        "today_summary": {
            "sessions_completed": today_completed,
            "sessions_interrupted": len(today_sessions) - today_completed,
            "total_focus_minutes": round(today_focus, 1),
        },
    }, indent=2)


@mcp.tool()
def get_stats(days: int = 7, api_key: str = "") -> str:
    """Get Pomodoro productivity statistics for the last N days (default 7)."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    if not _sessions:
        return json.dumps({"message": "No sessions recorded yet. Start your first Pomodoro!", "total_sessions": 0})
    days = max(1, min(days, 365))
    total_minutes = sum(s["actual_minutes"] for s in _sessions)
    completed = [s for s in _sessions if s["completed"]]
    interrupted = [s for s in _sessions if not s["completed"]]
    completion_rate = len(completed) / len(_sessions) * 100 if _sessions else 0
    # Task breakdown
    task_totals: dict[str, float] = defaultdict(float)
    for s in _sessions:
        task_totals[s["task"]] += s["actual_minutes"]
    top_tasks = sorted(task_totals.items(), key=lambda x: x[1], reverse=True)[:5]
    # Streaks
    avg_session = total_minutes / len(_sessions) if _sessions else 0
    return json.dumps({
        "period_days": days,
        "total_sessions": len(_sessions),
        "completed_sessions": len(completed),
        "interrupted_sessions": len(interrupted),
        "completion_rate_pct": round(completion_rate, 1),
        "total_focus_minutes": round(total_minutes, 1),
        "total_focus_hours": round(total_minutes / 60, 1),
        "average_session_minutes": round(avg_session, 1),
        "top_tasks": [{"task": t, "minutes": round(m, 1)} for t, m in top_tasks],
        "active_session": _active_session,
    }, indent=2)


@mcp.tool()
def configure_timer(work_minutes: int = 25, short_break: int = 5, long_break: int = 15, sessions_before_long: int = 4, api_key: str = "") -> str:
    """Configure Pomodoro timer durations. Customise work, short break, long break, and session count before long break."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    work_minutes = max(5, min(work_minutes, 120))
    short_break = max(1, min(short_break, 30))
    long_break = max(5, min(long_break, 60))
    sessions_before_long = max(2, min(sessions_before_long, 10))
    old_config = dict(_config)
    _config["work_minutes"] = work_minutes
    _config["short_break_minutes"] = short_break
    _config["long_break_minutes"] = long_break
    _config["sessions_before_long_break"] = sessions_before_long
    # Calculate a full cycle
    cycle_work = work_minutes * sessions_before_long
    cycle_breaks = short_break * (sessions_before_long - 1) + long_break
    cycle_total = cycle_work + cycle_breaks
    return json.dumps({
        "previous_config": old_config,
        "new_config": dict(_config),
        "full_cycle": {
            "work_minutes": cycle_work,
            "break_minutes": cycle_breaks,
            "total_minutes": cycle_total,
            "total_hours": round(cycle_total / 60, 1),
        },
        "message": f"Timer configured: {work_minutes}min work, {short_break}min short break, {long_break}min long break every {sessions_before_long} sessions.",
    }, indent=2)


@mcp.tool()
def get_productivity_report(api_key: str = "") -> str:
    """Generate a detailed productivity report with insights and recommendations."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    if not _sessions:
        return json.dumps({"message": "No data yet. Complete some Pomodoro sessions first!", "recommendations": ["Start with the default 25-minute timer", "Begin with 2-3 sessions per day"]})
    total = len(_sessions)
    completed = sum(1 for s in _sessions if s["completed"])
    total_min = sum(s["actual_minutes"] for s in _sessions)
    avg_min = total_min / total
    completion_rate = completed / total * 100
    # Insights
    insights = []
    if completion_rate >= 80:
        insights.append("Excellent completion rate! You stay focused well.")
    elif completion_rate >= 50:
        insights.append("Decent completion rate. Try removing distractions to improve.")
    else:
        insights.append("Many interrupted sessions. Consider shorter work durations.")
    if avg_min > _config["work_minutes"]:
        insights.append("You often work beyond your timer — consider longer sessions.")
    if avg_min < _config["work_minutes"] * 0.5:
        insights.append("Sessions are quite short. Try building up duration gradually.")
    # Recommendations
    recommendations = []
    if completion_rate < 70:
        recommendations.append(f"Try shorter sessions: {max(10, _config['work_minutes'] - 5)} minutes")
    if total < 4:
        recommendations.append("Aim for at least 4 sessions per day for momentum")
    recommendations.append("Take breaks seriously — they improve the next session")
    if total_min > 120:
        recommendations.append("Great volume! Consider tracking which tasks get the most focus")
    return json.dumps({
        "report": {
            "total_sessions": total,
            "completed": completed,
            "completion_rate_pct": round(completion_rate, 1),
            "total_focus_hours": round(total_min / 60, 1),
            "avg_session_minutes": round(avg_min, 1),
        },
        "insights": insights,
        "recommendations": recommendations,
        "config": dict(_config),
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
