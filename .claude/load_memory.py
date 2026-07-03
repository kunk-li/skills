#!/usr/bin/env python3
"""SessionStart hook: load project memory and emit as additionalContext.

Reads CLAUDE.md, ROADMAP.md, STATUS.md (full) + a DECISIONS.md index (just
the ## headers — full text is Read on demand, D-042), and the most recent
file in _sessions/, then emits a JSON object Claude Code understands to
inject the combined text into the new session as system context.

This script does NOT read stdin (SessionStart hooks send {} only). Output
must be a single JSON object on stdout with hookSpecificOutput.additionalContext.
"""

import json
import sys
from pathlib import Path

# Force UTF-8 stdout on Windows (default cp/gbk can't encode emoji and many CJK)
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
    pass

# Project root = the directory containing .claude/
ROOT = Path(__file__).parent.parent

# Order matters — CLAUDE.md is the canonical first read.
# DECISIONS.md is NOT here: it is 100KB and was 24% of every injection. It is
# now injected as a derived index (## headers only) via decisions_index(), full
# text Read on demand. See D-042.
FILES = ["CLAUDE.md", "ROADMAP.md", "STATUS.md"]


def read_file(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def latest_session(sessions_dir: Path) -> Path | None:
    if not sessions_dir.is_dir():
        return None
    candidates = sorted(sessions_dir.glob("*.md"))
    return candidates[-1] if candidates else None


def decisions_index(path: Path) -> str | None:
    """Derive a lightweight index of DECISIONS.md = its ## headers only.

    Single-source-of-truth safe (D-042/048-R08): the index is derived from
    DECISIONS.md at hook time, never a hand-maintained copy that could drift.
    Full text is Read on demand when a specific D-XXX matters.
    """
    content = read_file(path)
    if content is None:
        return None
    heads = [ln.rstrip() for ln in content.splitlines() if ln.startswith("## ")]
    if not heads:
        return None
    return "\n".join(heads)


def build_context() -> str:
    parts: list[str] = []
    parts.append(
        "# 🧠 Project Memory(自动通过 SessionStart hook 注入)\n\n"
        "下面是该项目的持久化上下文。**按 CLAUDE.md 顺序读完整体后再开始干活**。\n"
        "如果用户的请求与文件里的决策冲突,先指出冲突,不要默默推翻。"
    )

    for fname in FILES:
        path = ROOT / fname
        content = read_file(path)
        if content is None:
            continue
        parts.append(f"\n\n---\n\n# 📄 {fname}\n\n{content.rstrip()}")

    didx = decisions_index(ROOT / "DECISIONS.md")
    if didx:
        parts.append(
            "\n\n---\n\n# 📄 DECISIONS.md · 索引(只注入标题,全文按需 Read · D-042)\n\n"
            "**要决策或发现冲突前,先按 D-号 Read `DECISIONS.md` 全文那一条**——"
            "别凭标题推翻已决策项(CLAUDE.md 红线:查 DECISIONS 先)。\n\n"
            f"{didx}"
        )

    latest = latest_session(ROOT / "_sessions")
    if latest:
        content = read_file(latest)
        if content:
            parts.append(
                f"\n\n---\n\n# 📜 上一份 session 总结 · `_sessions/{latest.name}`\n\n"
                f"{content.rstrip()}"
            )

    parts.append(
        "\n\n---\n\n"
        "# ✅ Hook 加载完成\n\n"
        "你现在已经有完整的项目上下文。"
        "**第一句回复应该直接告诉用户 STATUS.md 里的「下一步」具体是什么**,"
        "而不是问他想做什么。"
    )

    return "".join(parts)


def main() -> int:
    try:
        context_text = build_context()
    except Exception as e:  # noqa: BLE001
        # Never break the session — emit empty context on failure
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": f"⚠️ load_memory.py failed: {e}",
            }
        }
        json.dump(output, sys.stdout, ensure_ascii=False)
        return 0

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context_text,
        }
    }
    json.dump(output, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
