#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-B2-approval/CHAIN/PLAT")
TARGETS = ["SKILL-PRESSURE-LEDGER.md", "BAR-INPUT-SIGNALS.md", "PLAT-COMPLETION-AUDIT.md"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()
    checks = []
    for rel in TARGETS:
        p = ROOT / rel
        checks.append((f"file:{rel}", p.exists() and bool(p.read_text(encoding="utf-8").strip()) if p.exists() else False))
    checks.append(("tokens:no-fold", "No fold at PLAT" in (ROOT / "SKILL-PRESSURE-LEDGER.md").read_text(encoding="utf-8")))
    checks.append(("tokens:bar", "No real hub-wflow runtime proof" in (ROOT / "BAR-INPUT-SIGNALS.md").read_text(encoding="utf-8")))
    failed = [name for name, ok in checks if not ok]
    summary = (
        "CODEX-B2-PLAT "
        f"status={'pass' if not failed else 'fail'} "
        f"targets={sum(1 for name, ok in checks[:len(TARGETS)] if ok)}/{len(TARGETS)} "
        f"checks={len(checks)-len(failed)}/{len(checks)} "
        f"failed={','.join(failed) if failed else '-'}"
    )
    print(summary)
    if not args.summary_line:
        for name, ok in checks:
            print(("PASS" if ok else "FAIL") + " " + name)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
