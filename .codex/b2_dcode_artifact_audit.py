#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-B2-approval/CHAIN/D-code")
CODE = ROOT / "production-code"
MAIN = CODE / "src/main/java/com/codex/oa/b2approval/B2ApprovalCore.java"
TEST = CODE / "src/test/java/com/codex/oa/b2approval/B2ApprovalCoreTest.java"
CLASSES = CODE / "target/classes"
TEST_CLASSES = CODE / "target/test-classes"


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def as_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def file_check(path: Path, name: str) -> Check:
    if not path.exists():
        return Check(f"file:{name}", False, f"missing {as_posix(path)}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return Check(f"file:{name}", False, f"empty {as_posix(path)}")
    return Check(f"file:{name}", True, f"{len(text.splitlines())} lines")


def token_check(path: Path, name: str, tokens: list[str]) -> Check:
    if not path.exists():
        return Check(f"tokens:{name}", False, f"missing {as_posix(path)}")
    text = path.read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in text]
    if missing:
        return Check(f"tokens:{name}", False, "missing tokens: " + " | ".join(missing))
    return Check(f"tokens:{name}", True, "required tokens present")


def run_compile_and_tests() -> tuple[Check, int]:
    CLASSES.mkdir(parents=True, exist_ok=True)
    TEST_CLASSES.mkdir(parents=True, exist_ok=True)
    commands = [
        ["javac", "-encoding", "UTF-8", "-d", str(CLASSES), str(MAIN)],
        ["javac", "-encoding", "UTF-8", "-cp", str(CLASSES), "-d", str(TEST_CLASSES), str(TEST)],
        [
            "java",
            "-cp",
            str(CLASSES) + os.pathsep + str(TEST_CLASSES),
            "com.codex.oa.b2approval.B2ApprovalCoreTest",
        ],
    ]
    last_output = ""
    for command in commands:
        proc = subprocess.run(command, cwd=str(CODE), text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=120)
        last_output = (proc.stdout or proc.stderr or "").strip()
        if proc.returncode != 0:
            return Check("javac-java", False, "command failed: " + " ".join(command) + " :: " + last_output), 0
    match = re.search(r"B2_APPROVAL_CORE_TESTS passed=(\d+)", last_output)
    tests = int(match.group(1)) if match else 0
    return Check("javac-java", tests >= 24, last_output or "no output"), tests


def build_checks() -> tuple[list[Check], int]:
    checks = [
        file_check(MAIN, "main"),
        file_check(TEST, "test"),
        file_check(ROOT / "D-CODE-IMPLEMENTATION-SUMMARY.md", "summary"),
        file_check(ROOT / "COMPILE-TEST-RESULT.txt", "compile-result"),
        token_check(MAIN, "main", [
            "WORK_CONTEXT_SWITCH_REQUIRED",
            "TOTP_REQUIRED_OR_INVALID",
            "IDEMPOTENCY_CONFLICT",
            "APPROVAL_VERSION_CONFLICT",
            "DUAL_SIGN_SAME_SIGNER_FORBIDDEN",
            "D4_DETAIL_VERSION_STALE",
            "AuditSink",
        ]),
        token_check(TEST, "test", [
            "testMissingTotpFailsClosed",
            "testWrongContextFails",
            "testIdempotentReplayReturnsCurrentResult",
            "testAuditFailClosed",
            "testAuditChainVerify",
        ]),
        token_check(ROOT / "D-CODE-IMPLEMENTATION-SUMMARY.md", "summary", [
            "guarded reference implementation only",
            "B2_APPROVAL_CORE_TESTS passed=24",
            "not as a production-ready OA patch",
        ]),
    ]
    compile_check, tests = run_compile_and_tests()
    checks.append(compile_check)
    return checks, tests


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()
    checks, tests = build_checks()
    failed = [check for check in checks if not check.ok]
    targets = 4
    target_passed = sum(1 for check in checks[:targets] if check.ok)
    summary = (
        "CODEX-B2-DCODE "
        f"status={'pass' if not failed else 'fail'} "
        f"targets={target_passed}/{targets} "
        f"checks={len(checks) - len(failed)}/{len(checks)} "
        f"tests={tests} "
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
