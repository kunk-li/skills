#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
CODEX = ROOT / ".codex"
STATE_PATH = CODEX / "oa_module_state.json"
MEMORY_PATH = CODEX / "MEMORY.md"


def as_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def load_state() -> dict[str, Any]:
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def latest_session() -> tuple[Path, str] | None:
    sessions_dir = ROOT / "_sessions"
    if not sessions_dir.is_dir():
        return None

    def sort_key(path: Path) -> tuple[str, int, float]:
        match = re.match(r"(\d{4}-\d{2}-\d{2})-session-(\d+)\.md$", path.name)
        if match:
            return match.group(1), int(match.group(2)), path.stat().st_mtime
        return "", -1, path.stat().st_mtime

    candidates = sorted(sessions_dir.glob("*.md"), key=sort_key)
    if not candidates:
        return None
    path = candidates[-1]
    content = read_text(path)
    if not content:
        return None
    return path, content


def latest_session_path() -> Path | None:
    sessions_dir = ROOT / "_sessions"
    if not sessions_dir.is_dir():
        return None

    def sort_key(path: Path) -> tuple[str, int, float]:
        match = re.match(r"(\d{4}-\d{2}-\d{2})-session-(\d+)\.md$", path.name)
        if match:
            return match.group(1), int(match.group(2)), path.stat().st_mtime
        return "", -1, path.stat().st_mtime

    candidates = sorted(sessions_dir.glob("*.md"), key=sort_key)
    return candidates[-1] if candidates else None


def governing_plan_excerpt() -> str | None:
    content = read_text(ROOT / "TOOL-HARDENING-PLAN.md")
    if not content:
        return None
    lines = content.splitlines()
    start = next((idx for idx, line in enumerate(lines) if line.startswith("## §0")), None)
    if start is None:
        return None
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if "### 旧快照" in lines[idx] or "### 旧乱码快照" in lines[idx]:
            end = idx
            break
        if lines[idx].startswith("## §") and not lines[idx].startswith("## §0"):
            end = idx
            break
    return "\n".join(lines[start:end]).strip()


def decisions_index() -> str | None:
    content = read_text(ROOT / "DECISIONS.md")
    if not content:
        return None
    heads = [line.rstrip() for line in content.splitlines() if line.startswith("## ")]
    return "\n".join(heads) if heads else None


def codex_operating_rules(state: dict[str, Any]) -> str:
    module_id = state.get("module_id", "UNKNOWN")
    total = state.get("total_status", "UNKNOWN")
    work_unit = state.get("work_unit", "UNKNOWN")
    next_step = state.get("next", "UNKNOWN")
    chain_root = state.get("chain_root", "")
    return "\n".join(
        [
            "- Write only inside `D:/work/资料/skills/` and `D:/projects/skills-pilot/`; external OA/project repos are read-only.",
            "- Always use full paths for produced or referenced artifacts.",
            "- STATUS is a cover-in-place snapshot, not a log; detailed history goes to `D:/work/资料/skills/_sessions/`.",
            f"- Current OA module state file is `{as_posix(STATE_PATH)}`.",
            f"- Current OA module tags: `OA_MODULE_ID={module_id}`, `OA_MODULE_TOTAL={total}`, `OA_MODULE_WORK_UNIT={work_unit}`, `OA_MODULE_NEXT={next_step}`.",
            f"- Current OA module chain root is `{chain_root}`.",
            "- A follow-up work unit must not be described as a full OA module rerun.",
            "- BAR-EVAL over D-060's 11 bars is the total judgment; CMP and phase audits are evidence only.",
            "- Codex context, gates, and ritual must be native under `D:/work/资料/skills/.codex/`; do not read, forward to, or scan other tools' private directories.",
            "- Do not claim tool readiness or discuss N until all 11 bars pass.",
        ]
    )


def build_context() -> str:
    state = load_state()
    module_id = state.get("module_id", "UNKNOWN")
    chain_root = state.get("chain_root", "")
    parts: list[str] = [
        "# Codex Project Memory\n\n"
        "This context is loaded by Codex-native hooks under `D:/work/资料/skills/.codex/`.\n"
        "Do not treat the latest user message as an isolated task; first align to the current mainline state."
    ]

    memory = read_text(MEMORY_PATH)
    if memory:
        parts.append(
            "\n\n---\n\n"
            "# Codex Durable Memory - Read First\n\n"
            f"{memory.rstrip()}"
        )

    plan = governing_plan_excerpt()
    if plan:
        parts.append(
            "\n\n---\n\n"
            "# Governing Plan - Read First\n\n"
            "This is the active cross-session plan position. Follow §0 before acting.\n\n"
            f"{plan}"
        )

    parts.append(f"\n\n---\n\n# Codex Operating Rules\n\n{codex_operating_rules(state)}")

    for name in ("ROADMAP.md", "STATUS.md"):
        content = read_text(ROOT / name)
        if content:
            parts.append(f"\n\n---\n\n# {name}\n\n{content.rstrip()}")

    didx = decisions_index()
    if didx:
        parts.append(
            "\n\n---\n\n# DECISIONS.md Index\n\n"
            "Read the full D-entry before changing a settled decision.\n\n"
            f"{didx}"
        )

    latest_path = latest_session_path()
    if latest_path:
        parts.append(
            f"\n\n---\n\n# Latest Session Pointer\n\n"
            f"Latest session record: `{as_posix(latest_path)}`.\n"
            "Use sessions only for traceback or detailed audit history. Reusable rules belong in `.codex/MEMORY.md` or DECISIONS."
        )

    parts.append(
        "\n\n---\n\n"
        "# Codex Start Rule\n\n"
        f"First align to `OA_MODULE_ID={module_id}` using `{as_posix(STATE_PATH)}`. "
        f"Current chain root is `{chain_root}`. "
        "Do not hardcode A3 in hooks or reports; A3 is only the current state instance. "
        "CMP is evidence only; final judgment is BAR-EVAL over D-060's 11 bars."
    )
    return "".join(parts)


def main() -> int:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": build_context(),
        }
    }
    json.dump(output, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
