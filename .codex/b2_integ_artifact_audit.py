#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-B2-approval/CHAIN/INTEG")
TARGETS = ["INTEGRATION-MATRIX.md", "RUNTIME-EVIDENCE-GAPS.csv", "INTEG-COMPLETION-AUDIT.md"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()
    checks = []
    for rel in TARGETS:
        path = ROOT / rel
        checks.append((f"file:{rel}", path.exists() and bool(path.read_text(encoding="utf-8").strip()) if path.exists() else False))
    matrix = (ROOT / "INTEGRATION-MATRIX.md").read_text(encoding="utf-8")
    gaps = (ROOT / "RUNTIME-EVIDENCE-GAPS.csv").read_text(encoding="utf-8")
    checks.append(("tokens:not-cleared", "not_cleared" in matrix))
    checks.append(("tokens:gaps", "GAP-B2-007" in gaps))
    failed = [name for name, ok in checks if not ok]
    summary = (
        "CODEX-B2-INTEG "
        f"status={'pass' if not failed else 'fail'} "
        f"targets={sum(1 for name, ok in checks[:len(TARGETS)] if ok)}/{len(TARGETS)} "
        f"checks={len(checks)-len(failed)}/{len(checks)} "
        "integration=not_cleared "
        f"failed={','.join(failed) if failed else '-'}"
    )
    print(summary)
    if not args.summary_line:
        for name, ok in checks:
            print(("PASS" if ok else "FAIL") + " " + name)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
