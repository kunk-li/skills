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

ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-B2-approval/CHAIN/OPS")
TARGETS = ["RUNBOOK.md", "MONITORING-CHECKS.csv", "INCIDENT-RESPONSE.md", "OPS-COMPLETION-AUDIT.md"]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()
    checks: list[Check] = []
    for rel in TARGETS:
        p = ROOT / rel
        checks.append(Check(f"file:{rel}", p.exists() and bool(text(rel).strip()) if p.exists() else False, rel))
    checks.append(Check("tokens:runbook", "not a production OA runbook" in text("RUNBOOK.md"), "boundary"))
    checks.append(Check("tokens:monitoring", "hub_wflow_bridge_errors" in text("MONITORING-CHECKS.csv"), "integration blocker"))
    checks.append(Check("tokens:incident", "wrong context can read or sign" in text("INCIDENT-RESPONSE.md"), "context incident"))
    failed = [c for c in checks if not c.ok]
    summary = (
        "CODEX-B2-OPS "
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
