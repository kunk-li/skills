#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Codex-owned audit for A3 INTEG artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

CHAIN = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN")
INTEG = CHAIN / "INTEG"
TARGETS = [
    "INTEG-EVIDENCE-MATRIX.csv",
    "INTEG-PHASE-CONTINUITY.csv",
    "INTEG-BLOCKER-ALIGNMENT.md",
    "INTEG-TOTAL-JUDGMENT-INPUT.md",
    "INTEG-COMPLETION-AUDIT.md",
    "INTEG-ARTIFACT-MANIFEST.json",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as fh:
        filtered = (line for line in fh if not line.startswith("#"))
        return sum(1 for _ in csv.DictReader(filtered))


def audit() -> dict[str, Any]:
    checks: list[dict[str, Any]] = [{"name": "integ-dir", "ok": INTEG.is_dir(), "detail": str(INTEG)}]
    for name in TARGETS:
        path = INTEG / name
        checks.append({"name": f"target:{name}", "ok": path.is_file(), "detail": str(path)})

    csv_rows = 0
    for name in ["INTEG-EVIDENCE-MATRIX.csv", "INTEG-PHASE-CONTINUITY.csv"]:
        path = INTEG / name
        if path.exists():
            rows = count_csv_rows(path)
            csv_rows += rows
            checks.append({"name": f"csv-nonempty:{name}", "ok": rows > 0, "detail": str(rows)})

    blocker_path = INTEG / "INTEG-BLOCKER-ALIGNMENT.md"
    if blocker_path.exists():
        text = read_text(blocker_path)
        for token in ["PEND-A3-02", "PEND-A3-03", "BRISK-002", "BRISK-006", "CMP is evidence only"]:
            checks.append({"name": f"blocker-token:{token}", "ok": token in text, "detail": blocker_path.name})

    input_path = INTEG / "INTEG-TOTAL-JUDGMENT-INPUT.md"
    if input_path.exists():
        text = read_text(input_path)
        checks.append({"name": "total-rule-present", "ok": "all 11" in text and "NO_GO" in text, "detail": input_path.name})

    manifest_path = INTEG / "INTEG-ARTIFACT-MANIFEST.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(read_text(manifest_path))
            checks.append({"name": "manifest-result", "ok": manifest.get("result") == "complete", "detail": str(manifest.get("result"))})
            checks.append({"name": "manifest-next", "ok": manifest.get("next") == "FIND4", "detail": str(manifest.get("next"))})
        except Exception as exc:  # noqa: BLE001
            checks.append({"name": "manifest-json", "ok": False, "detail": str(exc)})

    ok = all(item["ok"] for item in checks)
    return {
        "module": "A3-org",
        "status": "pass" if ok else "blocked",
        "targets": TARGETS,
        "checks": checks,
        "csv_rows": csv_rows,
    }


def summary(result: dict[str, Any]) -> str:
    total = len(result["checks"])
    passed = sum(1 for item in result["checks"] if item["ok"])
    existing = sum(1 for name in TARGETS if (INTEG / name).is_file())
    return (
        f"CODEX-A3-INTEG status={result['status']} "
        f"targets={existing}/{len(TARGETS)} checks={passed}/{total} "
        f"csv_rows={result['csv_rows']} blockers=4"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()

    result = audit()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.summary_line:
        print(summary(result))
    else:
        print(summary(result))
        for check in result["checks"]:
            print(f"{'OK' if check['ok'] else 'FAIL'} {check['name']}: {check['detail']}")
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
