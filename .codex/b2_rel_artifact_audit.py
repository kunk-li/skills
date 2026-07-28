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

ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-B2-approval/CHAIN/REL")
TARGETS = ["RELEASE-READINESS.md", "RELEASE-CHECKLIST.csv", "ROLLBACK-PLAN.md", "REL-COMPLETION-AUDIT.md"]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def check_file(rel: str) -> Check:
    path = ROOT / rel
    if not path.exists():
        return Check(f"file:{rel}", False, str(path))
    text = path.read_text(encoding="utf-8")
    return Check(f"file:{rel}", bool(text.strip()), f"{len(text.splitlines())} lines")


def check_tokens(rel: str, tokens: list[str]) -> Check:
    text = (ROOT / rel).read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in text]
    return Check(f"tokens:{rel}", not missing, "missing: " + "|".join(missing) if missing else "ok")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()
    checks = [check_file(rel) for rel in TARGETS]
    checks.extend([
        check_tokens("RELEASE-READINESS.md", ["NOT_DEPLOYABLE", "No deployment", "BAR-EVAL"]),
        check_tokens("RELEASE-CHECKLIST.csv", ["REL-B2-003", "fail", "block deployment"]),
        check_tokens("REL-COMPLETION-AUDIT.md", ["NOT_DEPLOYABLE", "correctly propagates no-go"]),
    ])
    failed = [check for check in checks if not check.ok]
    target_passed = sum(1 for check in checks[:len(TARGETS)] if check.ok)
    summary = (
        "CODEX-B2-REL "
        f"status={'pass' if not failed else 'fail'} "
        f"targets={target_passed}/{len(TARGETS)} "
        f"checks={len(checks)-len(failed)}/{len(checks)} "
        "verdict=NOT_DEPLOYABLE "
        f"failed={','.join(check.name for check in failed) if failed else '-'}"
    )
    print(summary)
    if not args.summary_line:
        for check in checks:
            print(("PASS" if check.ok else "FAIL") + f" {check.name}: {check.detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
