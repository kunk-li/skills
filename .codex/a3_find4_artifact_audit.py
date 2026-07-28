#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Codex-owned audit for A3 FIND4 artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

CHAIN = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN")
FIND4 = CHAIN / "FIND4"
TARGETS = [
    "FIND4-CANDIDATE-TRIAGE.csv",
    "FIND4-FANOUT-AB-DECISION.csv",
    "FIND4-LIBRARY-FOLD-RECOMMENDATION.md",
    "FIND4-COMPLETION-AUDIT.md",
    "FIND4-ARTIFACT-MANIFEST.json",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as fh:
        filtered = (line for line in fh if not line.startswith("#"))
        return sum(1 for _ in csv.DictReader(filtered))


def audit() -> dict[str, Any]:
    checks: list[dict[str, Any]] = [{"name": "find4-dir", "ok": FIND4.is_dir(), "detail": str(FIND4)}]
    for name in TARGETS:
        path = FIND4 / name
        checks.append({"name": f"target:{name}", "ok": path.is_file(), "detail": str(path)})

    candidate_count = 0
    fold_count = 0
    for name in ["FIND4-CANDIDATE-TRIAGE.csv", "FIND4-FANOUT-AB-DECISION.csv"]:
        path = FIND4 / name
        if path.exists():
            rows = count_csv_rows(path)
            if name.startswith("FIND4-CANDIDATE"):
                candidate_count = rows
            checks.append({"name": f"csv-nonempty:{name}", "ok": rows > 0, "detail": str(rows)})

    decision_path = FIND4 / "FIND4-FANOUT-AB-DECISION.csv"
    if decision_path.exists():
        with decision_path.open("r", encoding="utf-8", newline="") as fh:
            filtered = (line for line in fh if not line.startswith("#"))
            for row in csv.DictReader(filtered):
                if row.get("library_fold") == "yes":
                    fold_count += 1
        checks.append({"name": "no-unproven-folds", "ok": fold_count == 0, "detail": str(fold_count)})

    recommendation_path = FIND4 / "FIND4-LIBRARY-FOLD-RECOMMENDATION.md"
    if recommendation_path.exists():
        text = read_text(recommendation_path)
        checks.append({"name": "library-count-157", "ok": "157" in text and "no skill-library fold" in text, "detail": recommendation_path.name})

    manifest_path = FIND4 / "FIND4-ARTIFACT-MANIFEST.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(read_text(manifest_path))
            checks.append({"name": "manifest-result", "ok": manifest.get("result") == "complete", "detail": str(manifest.get("result"))})
            checks.append({"name": "manifest-next", "ok": manifest.get("next") == "BAR-EVAL", "detail": str(manifest.get("next"))})
            checks.append({"name": "manifest-library-count", "ok": manifest.get("library_count") == 157, "detail": str(manifest.get("library_count"))})
        except Exception as exc:  # noqa: BLE001
            checks.append({"name": "manifest-json", "ok": False, "detail": str(exc)})

    ok = all(item["ok"] for item in checks)
    return {
        "module": "A3-org",
        "status": "pass" if ok else "blocked",
        "targets": TARGETS,
        "checks": checks,
        "candidate_count": candidate_count,
        "fold_count": fold_count,
    }


def summary(result: dict[str, Any]) -> str:
    total = len(result["checks"])
    passed = sum(1 for item in result["checks"] if item["ok"])
    existing = sum(1 for name in TARGETS if (FIND4 / name).is_file())
    return (
        f"CODEX-A3-FIND4 status={result['status']} "
        f"targets={existing}/{len(TARGETS)} checks={passed}/{total} "
        f"candidates={result['candidate_count']} folds={result['fold_count']} library=157"
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
