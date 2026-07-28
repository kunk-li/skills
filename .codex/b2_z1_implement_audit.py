#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class JavaTarget:
    module: str
    root: Path
    main: Path
    test: Path
    test_class: str
    expected_stdout: str


TARGETS = [
    JavaTarget(
        module="B2-approval",
        root=Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-B2-approval/CHAIN/D-code/production-code-implement"),
        main=Path("src/main/java/com/codex/oa/b2approval/implement/B2ApprovalImplement.java"),
        test=Path("src/test/java/com/codex/oa/b2approval/implement/B2ApprovalImplementTest.java"),
        test_class="com.codex.oa.b2approval.implement.B2ApprovalImplementTest",
        expected_stdout="B2_APPROVAL_IMPLEMENT_TESTS passed=36",
    ),
    JavaTarget(
        module="Z1-watchdog",
        root=Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-Z1-watchdog/CHAIN/D-code/production-code-implement"),
        main=Path("src/main/java/com/skills/pilot/oa/watchdog/implement/Z1WatchdogImplement.java"),
        test=Path("src/test/java/com/skills/pilot/oa/watchdog/implement/Z1WatchdogImplementTest.java"),
        test_class="com.skills.pilot.oa.watchdog.implement.Z1WatchdogImplementTest",
        expected_stdout="Z1_WATCHDOG_IMPLEMENT_TESTS passed=70",
    ),
]

REQUIRED_TOKENS = [
    "artifact_contract.selected_mode=implement",
    "R_IMPL_COMPILE",
    "R_IMPL_TEST",
    "R_IMPL_NOSTUB",
    "R_IMPL_FAILSAFE",
    "R_IMPL_N180_HANDOFF_CONSUMED",
]

FORBIDDEN_TOKENS = [
    "guarded reference",
    "guarded_reference",
    "UnsupportedOperationException",
    "in-memory-only",
    "draft-only",
]


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def check_target(target: JavaTarget) -> tuple[int, list[str]]:
    checks = 0
    failures: list[str] = []

    main = target.root / target.main
    test = target.root / target.test
    for file in [main, test]:
        checks += 1
        if not file.exists():
            failures.append(f"{target.module}:missing:{file.as_posix()}")

    if failures:
        return checks, failures

    text = main.read_text(encoding="utf-8") + "\n" + test.read_text(encoding="utf-8")
    for token in REQUIRED_TOKENS:
        checks += 1
        if token not in text:
            failures.append(f"{target.module}:missing-token:{token}")
    for token in FORBIDDEN_TOKENS:
        checks += 1
        if token.lower() in text.lower():
            failures.append(f"{target.module}:forbidden-token:{token}")

    classes = target.root / "target" / "classes"
    test_classes = target.root / "target" / "test-classes"

    compile_main = run(["javac", "-encoding", "UTF-8", "-d", str(classes), str(main)], target.root)
    checks += 1
    if compile_main.returncode != 0:
        failures.append(f"{target.module}:javac-main:{compile_main.stdout.strip()[:500]}")
        return checks, failures

    compile_test = run(["javac", "-encoding", "UTF-8", "-cp", str(classes), "-d", str(test_classes), str(test)], target.root)
    checks += 1
    if compile_test.returncode != 0:
        failures.append(f"{target.module}:javac-test:{compile_test.stdout.strip()[:500]}")
        return checks, failures

    test_run = run(["java", "-cp", os.pathsep.join([str(classes), str(test_classes)]), target.test_class], target.root)
    checks += 1
    if test_run.returncode != 0:
        failures.append(f"{target.module}:java-test:{test_run.stdout.strip()[:500]}")
    checks += 1
    if target.expected_stdout not in test_run.stdout:
        failures.append(f"{target.module}:missing-test-output:{target.expected_stdout}")

    return checks, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()

    total_checks = 0
    failures: list[str] = []
    for target in TARGETS:
        checks, target_failures = check_target(target)
        total_checks += checks
        failures.extend(target_failures)

    status = "pass" if not failures else "fail"
    line = f"CODEX-B2-Z1-IMPLEMENT status={status} modules=2 checks={total_checks} failed={','.join(failures) if failures else '-'}"
    print(line)
    if not args.summary_line and failures:
        for failure in failures:
            print(failure)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
