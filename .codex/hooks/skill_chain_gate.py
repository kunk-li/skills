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

ROOT = Path(__file__).resolve().parents[2]
CODEX = ROOT / ".codex"
sys.path.insert(0, str(CODEX))

from oa_shakedown import build_report, module_gate_summary  # noqa: E402


def emit_hook(report: dict) -> None:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": (
                f"{module_gate_summary(report)}\n"
                f"Current module work unit: {report['work_unit']}; state total: {report['state_total']}; "
                f"computed total: {report['computed_total']}; next: {report['next']}. "
                "Do not describe a follow-up work unit as a full OA module rerun. "
                "BAR-EVAL over the 11 bars is the final judgment; CMP and phase audits are evidence only."
            ),
        }
    }
    if report["run_status"] != "pass":
        output["systemMessage"] = "Codex OA module gate failed; inspect oa_shakedown output before continuing."
    json.dump(output, sys.stdout, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--summary-line", action="store_true")
    parser.add_argument("--deep", action="store_true")
    parser.add_argument("--assert-pass", action="store_true")
    args = parser.parse_args()

    report = build_report(run_audits=args.deep)
    if args.json:
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
        print()
    elif args.summary_line:
        print(module_gate_summary(report))
    else:
        emit_hook(report)
    return 0 if (report["run_status"] == "pass" or not args.assert_pass) else 2


if __name__ == "__main__":
    raise SystemExit(main())
