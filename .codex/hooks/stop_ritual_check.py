#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from datetime import date
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
STATUS_PATH = ROOT / "STATUS.md"
PLAN_PATH = ROOT / "TOOL-HARDENING-PLAN.md"
MEMORY_PATH = ROOT / ".codex" / "MEMORY.md"
SESSIONS_DIR = ROOT / "_sessions"
COUNTERS_DIR = ROOT / ".codex" / "stop-counters"
COUNTERS_DIR.mkdir(parents=True, exist_ok=True)

NUDGE_AFTER_STOPS = 4
FRESH_MINUTES = 25
STATUS_MAX_LINES = 60
STATUS_MAX_BYTES = 20000


def read_stdin() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw else {}
    except Exception:
        return {}


def fresh(path: Path, minutes: int = FRESH_MINUTES) -> bool:
    return path.exists() and ((time.time() - path.stat().st_mtime) / 60) < minutes


def today_session_fresh() -> bool:
    today = date.today().isoformat()
    candidates = sorted(SESSIONS_DIR.glob(f"{today}-session-*.md"))
    return bool(candidates and fresh(candidates[-1]))


def status_bloat_reason() -> str | None:
    if not STATUS_PATH.exists():
        return "STATUS.md missing"
    raw = STATUS_PATH.read_bytes()
    if len(raw) > STATUS_MAX_BYTES:
        return f"STATUS.md is {len(raw)} bytes, above {STATUS_MAX_BYTES}"
    try:
        line_count = len(STATUS_PATH.read_text(encoding="utf-8").splitlines())
    except Exception:
        return "STATUS.md cannot be decoded as UTF-8"
    if line_count > STATUS_MAX_LINES:
        return f"STATUS.md has {line_count} lines, above {STATUS_MAX_LINES}"
    return None


def emit(reason: str) -> int:
    today = date.today().isoformat()
    output = {
        "systemMessage": f"Codex project ritual reminder: {reason}",
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": (
                f"Codex-native stop ritual check failed: {reason}\n\n"
                "Before finalizing, update the current-state files without turning STATUS into a log:\n"
                "- `D:/work/资料/skills/STATUS.md`: cover-update current state, keep it under one screen.\n"
                "- `D:/work/资料/skills/TOOL-HARDENING-PLAN.md`: update §0 if the mainline position changed.\n"
                f"- `D:/work/资料/skills/_sessions/{today}-session-N.md`: write the detailed session record.\n\n"
                f"- `{MEMORY_PATH.as_posix()}`: update reusable cross-session rules; sessions are audit history, not generic memory.\n\n"
                "Keep A3 judgment discipline: CMP is evidence only; BAR-EVAL must score D-060's 11 bars."
            ),
        },
    }
    json.dump(output, sys.stdout, ensure_ascii=False)
    return 0


def main() -> int:
    data = read_stdin()
    session_id = str(data.get("session_id") or "unknown")
    counter = COUNTERS_DIR / f"{session_id}.txt"
    try:
        stops = int(counter.read_text(encoding="utf-8")) if counter.exists() else 0
    except Exception:
        stops = 0
    stops += 1
    counter.write_text(str(stops), encoding="utf-8")

    if stops < NUDGE_AFTER_STOPS:
        return 0

    reasons: list[str] = []
    if not fresh(STATUS_PATH):
        reasons.append("STATUS.md stale")
    if not fresh(PLAN_PATH):
        reasons.append("TOOL-HARDENING-PLAN.md stale")
    if not today_session_fresh():
        reasons.append(f"no fresh _sessions/{date.today().isoformat()}-session-*.md")
    bloat = status_bloat_reason()
    if bloat:
        reasons.append(bloat)
    if not reasons:
        return 0
    return emit("; ".join(reasons))


if __name__ == "__main__":
    raise SystemExit(main())
