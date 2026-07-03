#!/usr/bin/env python3
"""Stop hook: nudge if STATUS.md hasn't been touched this session, or if
no session-N.md exists for today.

Strategy:
- Track per-session "stop count" in .claude/.stop-counters/<session_id>.txt
- Only nudge after the Nth stop (heuristic for "session winding down"), not
  every single turn
- Nudge via systemMessage (UI-visible warning) + additionalContext (injected
  back to model so Claude actually does the update)
- Once STATUS.md mtime advances past the session's start mtime, mark
  session as "ritual done" and stay quiet

This is intentionally conservative — better to nudge late than to nag
after every turn.
"""

import json
import os
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

# Force UTF-8 stdout on Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
    pass

ROOT = Path(__file__).parent.parent
STATUS_PATH = ROOT / "STATUS.md"
SESSIONS_DIR = ROOT / "_sessions"
COUNTERS_DIR = Path(__file__).parent / ".stop-counters"
COUNTERS_DIR.mkdir(exist_ok=True)

# Tunables
NUDGE_AFTER_STOPS = 6        # only nudge after N stops in this session (rough proxy for "long session")
STATUS_FRESH_MINUTES = 20    # if STATUS.md was modified within this window, consider it fresh
SESSION_FRESH_MINUTES = 30   # same for session files
STATUS_MAX_BYTES = 20000     # D-042: STATUS is a ≤1-screen snapshot; >20KB = bloat creeping back
STATUS_MAX_LINE_BYTES = 8000 # any single line this big = an append-log changelog creeping back


def silent_ok() -> int:
    """Exit successfully with no output (no nudge)."""
    return 0


def emit_nudge(reason: str) -> int:
    """Emit a JSON nudge that surfaces in UI + injects into Claude context."""
    today = date.today().isoformat()
    out = {
        "systemMessage": f"📝 Project ritual reminder: {reason}",
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": (
                f"⚠️ Project memory ritual check ({reason}).\n\n"
                f"Before continuing, please do these two things now:\n\n"
                f"1. **Update STATUS.md** at `D:/work/资料/skills/STATUS.md` — it is a "
                f"COVER-IN-PLACE snapshot, NOT an append log (D-042):\n"
                f"   - Bump '最后更新' to today\n"
                f"   - REPLACE stale current-state in-place; do NOT stack new notes on top\n"
                f"   - Sections are: 现在做什么 / 在途线程 / 卡点 / 按需细读指针\n"
                f"   - Superseded detail MOVES into today's _sessions (move, don't copy)\n"
                f"   - Keep STATUS ≤ one screen (~60 lines); if it grew, trim now\n\n"
                f"2. **Write a session summary** at "
                f"`D:/work/资料/skills/_sessions/{today}-session-N.md`\n"
                f"   - N = next number after the last file in _sessions/\n"
                f"   - This is the append-only history log; full detail goes HERE, not in STATUS\n\n"
                f"This is **automated by the Stop hook**; the human won't ask "
                f"and won't remember. You are the one who must do this."
            ),
        },
    }
    json.dump(out, sys.stdout, ensure_ascii=False)
    return 0


def main() -> int:
    # Read stdin to get session_id
    try:
        stdin_data = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        stdin_data = {}
    session_id = stdin_data.get("session_id", "unknown")

    # Per-session stop counter
    counter_path = COUNTERS_DIR / f"{session_id}.txt"
    n_stops = 0
    if counter_path.exists():
        try:
            n_stops = int(counter_path.read_text() or "0")
        except ValueError:
            n_stops = 0
    n_stops += 1
    counter_path.write_text(str(n_stops))

    # Only nudge after this session has stopped enough times to suggest
    # it's winding down (avoid nagging every turn)
    if n_stops < NUDGE_AFTER_STOPS:
        return silent_ok()

    # Check STATUS.md freshness
    status_fresh = False
    if STATUS_PATH.exists():
        age_min = (time.time() - STATUS_PATH.stat().st_mtime) / 60
        status_fresh = age_min < STATUS_FRESH_MINUTES

    # Check today's session file freshness
    today = date.today().isoformat()
    today_sessions = sorted(SESSIONS_DIR.glob(f"{today}-session-*.md"))
    session_fresh = False
    if today_sessions:
        latest = today_sessions[-1]
        age_min = (time.time() - latest.stat().st_mtime) / 60
        session_fresh = age_min < SESSION_FRESH_MINUTES

    # STATUS bloat check (D-042: snapshot must stay small; hook-enforce retention,
    # because discipline-in-doc has self-proven to rot). Fires even when STATUS is
    # "fresh" — a fresh-but-bloated STATUS means a changelog is creeping back.
    status_bloated = False
    bloat_reason = ""
    if STATUS_PATH.exists():
        raw = STATUS_PATH.read_bytes()
        if len(raw) > STATUS_MAX_BYTES:
            status_bloated = True
            bloat_reason = (
                f"STATUS.md is {len(raw)//1024}KB (>{STATUS_MAX_BYTES//1024}KB budget) "
                f"— it is a ≤1-screen snapshot, not a log; trim now and demote history to _sessions/"
            )
        else:
            for ln in raw.split(b"\n"):
                if len(ln) > STATUS_MAX_LINE_BYTES:
                    status_bloated = True
                    bloat_reason = (
                        f"STATUS.md has a {len(ln)//1024}KB single line — an append-log changelog "
                        f"is creeping back; move it to _sessions/ or _archive/"
                    )
                    break

    if status_fresh and session_fresh and not status_bloated:
        return silent_ok()

    # At least one is stale or STATUS is bloated — emit nudge
    reasons = []
    if not status_fresh:
        reasons.append("STATUS.md is stale")
    if not session_fresh:
        reasons.append(f"no fresh _sessions/{today}-session-*.md")
    if status_bloated:
        reasons.append(bloat_reason)
    return emit_nudge("; ".join(reasons))


if __name__ == "__main__":
    sys.exit(main())
