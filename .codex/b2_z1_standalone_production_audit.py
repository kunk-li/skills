#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/b2-z1-standalone-production-code")

REQUIRED = [
    "pom.xml",
    "RUNBOOK.md",
    "REFERENCE-ALIGNMENT.md",
    "VALIDATION-RESULT.md",
    "COMPILE-TEST-RESULT.txt",
    "OA2-OA1-GAP-ATTRIBUTION.md",
    "src/main/resources/application-oa2-local.properties",
    "src/main/resources/db/migration/V20260728_01__b2_shadow_approval.sql",
    "src/main/resources/db/migration/V20260728_02__z1_shadow_watchdog.sql",
    "src/main/java/com/hub/oa/sys/modular/approval/controller/OaTicketWriteController.java",
    "src/main/java/com/hub/oa/sys/modular/approval/controller/ApprovalWflowCallbackController.java",
    "src/main/java/com/hub/oa/sys/modular/approval/transfer/controller/ApprovalTransferShadowController.java",
    "src/main/java/com/hub/oa/sys/modular/approval/service/impl/OaTicketWriteServiceImpl.java",
    "src/main/java/com/hub/oa/sys/modular/approval/mapper/OaTicketMapper.java",
    "src/main/java/com/hub/oa/sys/modular/watchdog/controller/OaWatchdogShadowController.java",
    "src/main/java/com/hub/oa/sys/modular/watchdog/service/impl/Z1WatchdogDeployableServiceImpl.java",
    "src/main/java/com/hub/oa/sys/modular/watchdog/mapper/Z1WatchdogMapper.java",
    "src/main/java/com/hub/oa/standalone/Oa2StandaloneApplication.java",
    "src/main/java/com/hub/oa/standalone/Oa2SmokeRunner.java",
    "src/main/java/com/hub/oa/standalone/runtime/Oa2Runtime.java",
    "src/main/java/com/hub/oa/standalone/runtime/Oa2RuntimeConfig.java",
    "src/main/java/com/hub/oa/standalone/runtime/InMemoryApprovalStore.java",
    "src/main/java/com/hub/oa/standalone/runtime/InMemoryZ1Store.java",
    "src/main/java/com/hub/oa/standalone/runtime/LocalWflowGateway.java",
    "src/main/java/com/hub/oa/standalone/runtime/LocalTotpVerifier.java",
    "src/main/java/com/hub/oa/standalone/runtime/LocalKmsAdapter.java",
    "src/main/java/com/hub/oa/standalone/runtime/LocalAlertCenterAdapter.java",
    "src/main/java/com/hub/oa/standalone/runtime/LocalRadarSourceAdapter.java",
    "src/test/java/com/hub/oa/standalone/B2Z1StandaloneProductionTest.java",
]

REQUIRED_TOKENS = [
    "OA1",
    "OA2",
    "两个完全独立的系统",
    "OA2_SELF_CONTAINED_SMOKE passed=16",
    "OA2_HTTP_SMOKE status=200",
    "Oa2StandaloneApplication",
    "application-oa2-local.properties",
    "mvn -q -DskipTests package",
    "HttpServer",
    "self-contained runnable package",
    "WflowGatewayPort",
    "TotpVerifyPort",
    "ApprovalTransferEligibilityService",
    "Z1WatchdogDeployableService",
    "KmsPort",
    "AlertCenterPort",
    "RadarSourcePort",
    "CREATE TABLE IF NOT EXISTS OA_APPROVAL_AUDIT_EVENT",
    "CREATE TABLE IF NOT EXISTS OA_COMPLAINT_AUDIT_TICKET",
]

FORBIDDEN = [
    "UnsupportedOperationException",
    "guarded reference",
    "in-memory-only",
    "patch/diff",
    "映射到真实 hub-oa",
    "逐文件映射到真实 hub-oa",
    "真实 hub-oa 目标路径",
    "编入 hub-oa",
]

EXCLUDED_SCAN_DIRS = {
    "FOLD-060-093-SELF-CONTAINED-RUNTIME",
    "FOLD-061-066-088-101-RUNTIME-BOUNDARY-CHAIN",
    "FOLD-GENERICITY-CLEANUP",
    "FOLD-FEATURE-DEPTH-BATCH",
}


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    try:
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
    except FileNotFoundError as ex:
        return subprocess.CompletedProcess(cmd, 127, stdout=str(ex))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()

    checks = 0
    failures: list[str] = []

    for rel in REQUIRED:
        checks += 1
        if not (ROOT / rel).exists():
            failures.append(f"missing:{rel}")

    text = ""
    if ROOT.exists():
        for path in ROOT.rglob("*"):
            if any(part in EXCLUDED_SCAN_DIRS for part in path.parts):
                continue
            if path.is_file() and path.suffix in {".java", ".md", ".sql", ".txt"}:
                text += "\n" + path.read_text(encoding="utf-8", errors="replace")
            elif path.is_file() and path.suffix in {".xml", ".properties"}:
                text += "\n" + path.read_text(encoding="utf-8", errors="replace")

    for token in REQUIRED_TOKENS:
        checks += 1
        if token not in text:
            failures.append(f"missing-token:{token}")
    for token in FORBIDDEN:
        checks += 1
        if token.lower() in text.lower():
            failures.append(f"forbidden-token:{token}")

    main_files = [str(p) for p in (ROOT / "src/main/java").rglob("*.java")]
    test_files = [str(p) for p in (ROOT / "src/test/java").rglob("*.java")]
    checks += 1
    if len(main_files) < 20:
        failures.append(f"too-few-main-java:{len(main_files)}")
    checks += 1
    if len(test_files) < 1:
        failures.append("missing-test-java")

    if not failures:
        classes = ROOT / "target/classes"
        test_classes = ROOT / "target/test-classes"
        for build_dir in (classes, test_classes):
            if build_dir.exists():
                shutil.rmtree(build_dir)
        c1 = run(["javac", "-encoding", "UTF-8", "-d", str(classes), *main_files], ROOT)
        checks += 1
        if c1.returncode != 0:
            failures.append("javac-main:" + c1.stdout.strip()[:500])
        else:
            c2 = run(["javac", "-encoding", "UTF-8", "-cp", str(classes), "-d", str(test_classes), *test_files], ROOT)
            checks += 1
            if c2.returncode != 0:
                failures.append("javac-test:" + c2.stdout.strip()[:500])
            else:
                cp = os.pathsep.join([str(classes), str(test_classes)])
                c3 = run(["java", "-cp", cp, "com.hub.oa.standalone.B2Z1StandaloneProductionTest"], ROOT)
                checks += 1
                if c3.returncode != 0:
                    failures.append("java-test:" + c3.stdout.strip()[:500])
                checks += 1
                if "B2_Z1_STANDALONE_PRODUCTION_TESTS passed=21" not in c3.stdout:
                    failures.append("missing-test-output")
                c4 = run(["java", "-cp", str(classes), "com.hub.oa.standalone.Oa2StandaloneApplication", "--smoke"], ROOT)
                checks += 1
                if c4.returncode != 0:
                    failures.append("oa2-smoke:" + c4.stdout.strip()[:500])
                checks += 1
                if "OA2_SELF_CONTAINED_SMOKE passed=16" not in c4.stdout:
                    failures.append("missing-oa2-smoke-output")
                c4b = run(["java", "-cp", str(classes), "com.hub.oa.standalone.Oa2StandaloneApplication", "--http-smoke"], ROOT)
                checks += 1
                if c4b.returncode != 0:
                    failures.append("oa2-http-smoke:" + c4b.stdout.strip()[:500])
                checks += 1
                if "OA2_HTTP_SMOKE status=200" not in c4b.stdout:
                    failures.append("missing-oa2-http-smoke-output")
                mvn = "mvn.cmd" if os.name == "nt" else "mvn"
                c5 = run([mvn, "-q", "-DskipTests", "package"], ROOT)
                checks += 1
                if c5.returncode != 0:
                    failures.append("maven-package:" + c5.stdout.strip()[:500])
                jar = ROOT / "target/oa2-standalone-production-code-0.1.0-shakedown.jar"
                checks += 1
                if not jar.exists():
                    failures.append("missing-jar")
                elif c5.returncode == 0:
                    c6 = run(["java", "-jar", str(jar), "--smoke"], ROOT)
                    checks += 1
                    if c6.returncode != 0:
                        failures.append("jar-smoke:" + c6.stdout.strip()[:500])
                    checks += 1
                    if "OA2_SELF_CONTAINED_SMOKE passed=16" not in c6.stdout:
                        failures.append("missing-jar-smoke-output")
                    c7 = run(["java", "-jar", str(jar), "--http-smoke"], ROOT)
                    checks += 1
                    if c7.returncode != 0:
                        failures.append("jar-http-smoke:" + c7.stdout.strip()[:500])
                    checks += 1
                    if "OA2_HTTP_SMOKE status=200" not in c7.stdout:
                        failures.append("missing-jar-http-smoke-output")

    status = "pass" if not failures else "fail"
    print(f"CODEX-B2-Z1-STANDALONE-PRODUCTION status={status} checks={checks} failed={','.join(failures) if failures else '-'}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
