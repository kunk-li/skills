#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-B2-approval/CHAIN/TEST")
DCODE_AUDIT = Path("D:/work/资料/skills/.codex/b2_dcode_artifact_audit.py")


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def as_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


TARGETS = [
    "TEST-STRATEGY.md",
    "TEST-CASE-MATRIX.md",
    "TEST-CASE-MATRIX.csv",
    "AUTOMATION-RESULT.md",
    "QUALITY-GATE-TEST.md",
]


def file_check(rel: str) -> Check:
    path = ROOT / rel
    if not path.exists():
        return Check(f"file:{rel}", False, f"missing {as_posix(path)}")
    text = path.read_text(encoding="utf-8")
    return Check(f"file:{rel}", bool(text.strip()), f"{len(text.splitlines())} lines")


def token_check(rel: str, tokens: list[str]) -> Check:
    path = ROOT / rel
    if not path.exists():
        return Check(f"tokens:{rel}", False, f"missing {as_posix(path)}")
    text = path.read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in text]
    if missing:
        return Check(f"tokens:{rel}", False, "missing tokens: " + " | ".join(missing))
    return Check(f"tokens:{rel}", True, "required tokens present")


def dcode_rerun_check() -> Check:
    proc = subprocess.run(
        [sys.executable, str(DCODE_AUDIT), "--summary-line"],
        cwd="D:/work/资料/skills",
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=180,
    )
    output = (proc.stdout or proc.stderr or "").strip()
    ok = proc.returncode == 0 and "CODEX-B2-DCODE status=pass" in output and "tests=24" in output
    return Check("dcode-rerun", ok, output)


def build_checks() -> list[Check]:
    checks = [file_check(rel) for rel in TARGETS]
    checks.extend(
        [
            token_check("TEST-STRATEGY.md", ["constrained_pass", "hub-wflow integration", "not cleared"]),
            token_check("TEST-CASE-MATRIX.csv", ["TC-B2-001", "TC-B2-018", "not_cleared"]),
            token_check("AUTOMATION-RESULT.md", ["B2_APPROVAL_CORE_TESTS passed=24", "CODEX-B2-DCODE status=pass"]),
            token_check("QUALITY-GATE-TEST.md", ["constrained_pass", "TEST-BLOCK-B2-005", "BAR-EVAL remains pending"]),
            dcode_rerun_check(),
        ]
    )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()
    checks = build_checks()
    failed = [check for check in checks if not check.ok]
    target_passed = sum(1 for check in checks[: len(TARGETS)] if check.ok)
    summary = (
        "CODEX-B2-TEST "
        f"status={'pass' if not failed else 'fail'} "
        f"targets={target_passed}/{len(TARGETS)} "
        f"checks={len(checks) - len(failed)}/{len(checks)} "
        "gate=constrained_pass "
        f"failed={','.join(check.name for check in failed) if failed else '-'}"
    )
    if args.summary_line:
        print(summary)
    else:
        print(summary)
        for check in checks:
            print(("PASS" if check.ok else "FAIL") + f" {check.name}: {check.detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
