#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-B2-approval/CHAIN/DOC")
TARGETS = ["HANDOFF.md", "API-HANDOFF.md", "DATA-HANDOFF.md", "KNOWN-BLOCKERS.md", "DOC-COMPLETION-AUDIT.md"]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def t(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()
    checks = []
    for rel in TARGETS:
        path = ROOT / rel
        checks.append(Check(f"file:{rel}", path.exists() and bool(t(rel).strip()) if path.exists() else False, rel))
    checks.append(Check("tokens:handoff", "guarded reference" in t("HANDOFF.md"), "guarded reference"))
    checks.append(Check("tokens:blockers", "DOC-B2-005" in t("KNOWN-BLOCKERS.md"), "runtime blocker"))
    failed = [c for c in checks if not c.ok]
    summary = (
        "CODEX-B2-DOC "
        f"status={'pass' if not failed else 'fail'} "
        f"targets={sum(1 for c in checks[:len(TARGETS)] if c.ok)}/{len(TARGETS)} "
        f"checks={len(checks)-len(failed)}/{len(checks)} "
        f"failed={','.join(c.name for c in failed) if failed else '-'}"
    )
    print(summary)
    if not args.summary_line:
        for c in checks:
            print(("PASS" if c.ok else "FAIL") + f" {c.name}: {c.detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
