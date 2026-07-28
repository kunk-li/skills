#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-B2-approval/CHAIN/BAR-EVAL")
JSON_PATH = ROOT / "BAR-EVAL-11BAR-SCORECARD.json"
MD_PATH = ROOT / "BAR-EVAL-11BAR-SCORECARD.md"
AUDIT_PATH = ROOT / "BAR-EVAL-COMPLETION-AUDIT.md"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()
    checks = []
    for path in [JSON_PATH, MD_PATH, AUDIT_PATH]:
        checks.append((f"file:{path.name}", path.exists() and bool(path.read_text(encoding="utf-8").strip()) if path.exists() else False))
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    bars = data.get("bars", [])
    passed = sum(1 for b in bars if str(b.get("status", "")).upper() == "PASS")
    partial = sum(1 for b in bars if str(b.get("status", "")).upper() == "PARTIAL")
    fail = sum(1 for b in bars if str(b.get("status", "")).upper() == "FAIL")
    checks.append(("bars:count", len(bars) == 11))
    checks.append(("bars:verdict", data.get("verdict") == "NO_GO"))
    checks.append(("bars:not-all-pass", passed < 11 and fail >= 1))
    failed = [name for name, ok in checks if not ok]
    summary = (
        "CODEX-B2-BAR-EVAL "
        f"status={'pass' if not failed else 'fail'} "
        f"targets={sum(1 for name, ok in checks[:3] if ok)}/3 "
        f"checks={len(checks)-len(failed)}/{len(checks)} "
        f"bars={passed}/11 partial={partial} fail={fail} verdict={data.get('verdict')} "
        f"failed={','.join(failed) if failed else '-'}"
    )
    print(summary)
    if not args.summary_line:
        for name, ok in checks:
            print(("PASS" if ok else "FAIL") + " " + name)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
