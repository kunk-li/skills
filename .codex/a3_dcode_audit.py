#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Codex-owned physical audit for A3 D-code Maven deliverables."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


DEFAULT_CHAIN_ROOT = Path(
    "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN"
)
MVN = shutil.which("mvn.cmd" if os.name == "nt" else "mvn") or shutil.which("mvn") or "mvn"

STUB_PATTERNS = [
    ("TODO", re.compile(r"\bTODO\b", re.IGNORECASE)),
    ("FIXME", re.compile(r"\bFIXME\b", re.IGNORECASE)),
    ("UnsupportedOperationException", re.compile(r"UnsupportedOperationException")),
    ("not implemented", re.compile(r"not\s+implemented", re.IGNORECASE)),
    ("placeholder", re.compile(r"placeholder", re.IGNORECASE)),
    ("stub", re.compile(r"\bstub\b", re.IGNORECASE)),
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def java_files(project: Path) -> list[Path]:
    src = project / "src"
    if not src.exists():
        return []
    return sorted(p for p in src.rglob("*.java") if p.is_file())


def discover_projects(d_code_root: Path, label: str) -> list[Path]:
    root = d_code_root / label
    if (root / "pom.xml").is_file():
        return [root]
    projects = []
    for pom in root.rglob("pom.xml"):
        if "target" not in pom.parts:
            projects.append(pom.parent)
    return sorted(projects)


def scan_no_stub(files: list[Path]) -> list[str]:
    hits = []
    for java_file in files:
        for line_no, line in enumerate(read_text(java_file).splitlines(), start=1):
            for name, pattern in STUB_PATTERNS:
                if pattern.search(line):
                    hits.append(f"{java_file}:{line_no}:{name}")
                    break
    return hits


def run(command: list[str], cwd: Path, timeout: int) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return proc.returncode, (proc.stdout + proc.stderr)
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired as exc:
        return 124, (exc.stdout or "") + (exc.stderr or f"timeout after {timeout}s")


def count_surefire_tests(project: Path) -> int:
    total = 0
    for report in (project / "target" / "surefire-reports").glob("TEST-*.xml"):
        try:
            root = ET.parse(report).getroot()
        except ET.ParseError:
            continue
        total += int(float(root.attrib.get("tests", "0")))
    return total


def audit_project(label: str, project: Path, timeout: int) -> dict[str, Any]:
    files = java_files(project)
    result: dict[str, Any] = {
        "label": label,
        "project": str(project),
        "java_files": len(files),
        "stub_hits": [],
        "mvn_test": "not_run",
        "surefire_tests": 0,
        "status": "blocked",
        "reason": "",
    }

    if not files:
        result["reason"] = "no src Java files"
        return result

    stub_hits = scan_no_stub(files)
    result["stub_hits"] = stub_hits
    if stub_hits:
        result["reason"] = f"no-stub scan failed: {len(stub_hits)} hits"
        return result

    code, output = run([MVN, "clean", "test"], project, timeout)
    result["mvn_test"] = "pass" if code == 0 else "fail"
    if code != 0:
        result["reason"] = output.strip()[-1200:]
        return result

    test_count = count_surefire_tests(project)
    result["surefire_tests"] = test_count
    if test_count <= 0:
        result["reason"] = "mvn test produced zero Surefire tests"
        return result

    result["status"] = "pass"
    result["reason"] = "mvn clean test passed with nonzero tests and no stubs"
    return result


def audit(chain_root: Path, timeout: int) -> dict[str, Any]:
    d_code_root = chain_root / "D-code"
    projects = []
    for label in ("production-code", "gen"):
        for project in discover_projects(d_code_root, label):
            projects.append((label, project))

    if not projects:
        return {
            "module": "A3",
            "chain_root": str(chain_root),
            "status": "blocked",
            "reason": "no Maven projects found under D-code/production-code or D-code/gen",
            "projects": [],
        }

    project_results = [audit_project(label, project, timeout) for label, project in projects]
    has_production = any(r["label"] == "production-code" for r in project_results)
    all_pass = has_production and all(r["status"] == "pass" for r in project_results)
    return {
        "module": "A3",
        "chain_root": str(chain_root),
        "status": "pass" if all_pass else "blocked",
        "reason": "D-code Maven physical audit passed" if all_pass else "one or more D-code projects failed physical audit",
        "projects": project_results,
    }


def summary(result: dict[str, Any]) -> str:
    total = len(result["projects"])
    passed = sum(1 for p in result["projects"] if p["status"] == "pass")
    tests = sum(int(p.get("surefire_tests", 0)) for p in result["projects"])
    java = sum(int(p.get("java_files", 0)) for p in result["projects"])
    return (
        f"CODEX-A3-DCODE status={result['status']} "
        f"projects={passed}/{total} java={java} surefire_tests={tests}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chain-root", default=str(DEFAULT_CHAIN_ROOT))
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()

    result = audit(Path(args.chain_root), args.timeout)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.summary_line:
        print(summary(result))
    else:
        print(summary(result))
        for project in result["projects"]:
            print(
                "{label}:{project} status={status} java={java_files} tests={surefire_tests} reason={reason}".format(
                    **project
                )
            )
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
