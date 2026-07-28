#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Codex-owned artifact audit for A3 TEST (N230-N260)."""

from __future__ import annotations

import argparse
import csv
import json
import zipfile
from pathlib import Path
from typing import Any


DEFAULT_CHAIN_ROOT = Path(
    "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN"
)

EXPECTED = {
    "测试点清单.csv": {"min_rows": 20, "contains": "test-point-generation"},
    "测试用例集.xlsx": {"xlsx_contains": "TC-A3-CHG-005"},
    "边界条件清单.csv": {"min_rows": 10, "contains": "boundary-condition-generation"},
    "异常场景清单.csv": {"min_rows": 8, "contains": "exception-scenario-generation"},
    "回归测试清单.csv": {"min_rows": 20, "contains": "regression-test-checklist-generation"},
    "冒烟测试清单.csv": {"min_rows": 8, "contains": "smoke-test-checklist-generation"},
    "接口测试脚本.zip": {"zip_contains": "api-test-script-generation"},
    "自动化触发建议.md": {"contains": "test-automation-trigger-recommendation"},
    "自动化测试编排.yaml": {"contains": "test-automation-orchestration"},
    "test-failure-attribution.md": {"contains": "test-failure-attribution"},
    "defect-classification.csv": {"min_rows": 4, "contains": "defect-classification"},
    "defect-severity-assessment.csv": {"min_rows": 4, "contains": "defect-severity-assessment"},
    "defect-reproduction-steps.md": {"contains": "defect-reproduction-steps-generation"},
    "质量门禁检查单.md": {"contains": "quality-gate-check"},
    "上线前检查清单.csv": {"min_rows": 6, "contains": "pre-launch-checklist-generation"},
    "数据一致性检查项.csv": {"min_rows": 4, "contains": "data-consistency-check-item-generation"},
    "权限测试点.csv": {"min_rows": 5, "contains": "permission-test-point-generation"},
    "并发测试点.csv": {"min_rows": 4, "contains": "concurrency-test-point-generation"},
    "幂等测试点.csv": {"min_rows": 4, "contains": "idempotency-test-point-generation"},
    "性能测试场景.csv": {"min_rows": 4, "contains": "performance-test-scenario-generation"},
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return max(0, sum(1 for _ in csv.DictReader(f)))


def zip_text(path: Path) -> str:
    chunks: list[str] = []
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if name.endswith((".md", ".json", ".http", ".yaml", ".yml", ".csv")):
                chunks.append(zf.read(name).decode("utf-8", "ignore"))
    return "\n".join(chunks)


def xlsx_text(path: Path) -> str:
    chunks: list[str] = []
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if name.endswith(".xml") and ("sharedStrings" in name or "worksheets" in name):
                chunks.append(zf.read(name).decode("utf-8", "ignore"))
    return "\n".join(chunks)


def audit_file(test_dir: Path, name: str, spec: dict[str, Any]) -> dict[str, Any]:
    path = test_dir / name
    result = {"file": str(path), "target": name, "status": "pass", "reason": ""}
    if not path.is_file():
        result["status"] = "missing"
        result["reason"] = "file missing"
        return result
    if path.stat().st_size <= 0:
        result["status"] = "blocked"
        result["reason"] = "empty file"
        return result
    if "min_rows" in spec:
        rows = count_csv_rows(path)
        result["rows"] = rows
        if rows < int(spec["min_rows"]):
            result["status"] = "blocked"
            result["reason"] = f"csv rows {rows} < {spec['min_rows']}"
            return result
    if "contains" in spec:
        text = read_text(path)
        if spec["contains"] not in text:
            result["status"] = "blocked"
            result["reason"] = f"missing marker {spec['contains']}"
            return result
    if "zip_contains" in spec:
        text = zip_text(path)
        if spec["zip_contains"] not in text:
            result["status"] = "blocked"
            result["reason"] = f"zip missing marker {spec['zip_contains']}"
            return result
    if "xlsx_contains" in spec:
        text = xlsx_text(path)
        if spec["xlsx_contains"] not in text:
            result["status"] = "blocked"
            result["reason"] = f"xlsx missing marker {spec['xlsx_contains']}"
            return result
    return result


def audit(chain_root: Path) -> dict[str, Any]:
    test_dir = chain_root / "TEST"
    results = [audit_file(test_dir, name, spec) for name, spec in EXPECTED.items()]
    passed = sum(1 for r in results if r["status"] == "pass")
    return {
        "module": "A3",
        "phase": "TEST",
        "chain_root": str(chain_root),
        "test_dir": str(test_dir),
        "status": "pass" if passed == len(EXPECTED) else "blocked",
        "targets_passed": passed,
        "targets_total": len(EXPECTED),
        "results": results,
    }


def summary(result: dict[str, Any]) -> str:
    return (
        f"CODEX-A3-TEST status={result['status']} "
        f"targets={result['targets_passed']}/{result['targets_total']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chain-root", default=str(DEFAULT_CHAIN_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()
    result = audit(Path(args.chain_root))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(summary(result))
        if not args.summary_line:
            for item in result["results"]:
                print(f"{item['target']}: {item['status']} {item.get('reason','')}")
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
