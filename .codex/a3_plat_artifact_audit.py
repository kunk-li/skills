#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Codex-owned audit for A3 PLAT(N370-N390) artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

CHAIN = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN")
PLAT = CHAIN / "PLAT"

TARGETS = [
    "Skill路由记录.md",
    "Skill路由决策表.csv",
    "上下文记忆记录.md",
    "上下文记忆快照.md",
    "多Skill编排记录.md",
    "多skill执行计划.yaml",
    "状态机编排记录.md",
    "状态机流转记录.csv",
    "门禁放行记录.csv",
    "失败兜底切换记录.csv",
    "人工确认节点清单.csv",
    "审计留痕日志.csv",
    "模板库索引.csv",
    "质量评分结果.csv",
    "PLAT-COMPLETION-AUDIT.md",
    "PLAT-ARTIFACT-MANIFEST.json",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def count_csv_rows(path: Path) -> int:
    rows = 0
    with path.open("r", encoding="utf-8", newline="") as fh:
        filtered = (line for line in fh if not line.startswith("#"))
        reader = csv.DictReader(filtered)
        for _ in reader:
            rows += 1
    return rows


def audit() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    checks.append({"name": "plat-dir", "ok": PLAT.is_dir(), "detail": str(PLAT)})
    for name in TARGETS:
        path = PLAT / name
        checks.append({"name": f"target:{name}", "ok": path.is_file(), "detail": str(path)})

    csv_rows = 0
    markdown_count = 0
    yaml_present = False
    if PLAT.is_dir():
        for path in PLAT.iterdir():
            if path.suffix.lower() == ".csv":
                try:
                    rows = count_csv_rows(path)
                    csv_rows += rows
                    checks.append({"name": f"csv-nonempty:{path.name}", "ok": rows > 0, "detail": str(rows)})
                except Exception as exc:  # noqa: BLE001
                    checks.append({"name": f"csv-readable:{path.name}", "ok": False, "detail": str(exc)})
            if path.suffix.lower() == ".md":
                markdown_count += 1
                text = read_text(path)
                checks.append({"name": f"contract:{path.name}", "ok": "artifact_contract:" in text, "detail": path.name})
            if path.suffix.lower() in {".yaml", ".yml"}:
                yaml_present = True
                text = read_text(path)
                checks.append({"name": f"yaml-plan:{path.name}", "ok": "BAR-EVAL" in text and "INTEG" in text, "detail": path.name})

    audit_path = PLAT / "PLAT-COMPLETION-AUDIT.md"
    if audit_path.exists():
        text = read_text(audit_path)
        checks.append({"name": "audit-total-not-done", "ok": "不是 A3 总判定" in text and "NOT_DONE" in text, "detail": audit_path.name})
        checks.append({"name": "audit-next-integ", "ok": "下一步是 `INTEG`" in text or "下一步是 INTEG" in text, "detail": audit_path.name})

    manifest_path = PLAT / "PLAT-ARTIFACT-MANIFEST.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(read_text(manifest_path))
            checks.append({"name": "manifest-total", "ok": manifest.get("total_verdict") == "NOT_DONE", "detail": str(manifest.get("total_verdict"))})
            checks.append({"name": "manifest-next", "ok": manifest.get("next") == "INTEG", "detail": str(manifest.get("next"))})
        except Exception as exc:  # noqa: BLE001
            checks.append({"name": "manifest-json", "ok": False, "detail": str(exc)})

    ok = all(item["ok"] for item in checks)
    return {
        "module": "A3",
        "chain_root": str(CHAIN),
        "plat_dir": str(PLAT),
        "status": "pass" if ok else "blocked",
        "targets": TARGETS,
        "checks": checks,
        "csv_rows": csv_rows,
        "markdown_count": markdown_count,
        "yaml_present": yaml_present,
    }


def summary(result: dict[str, Any]) -> str:
    total = len(result["checks"])
    passed = sum(1 for item in result["checks"] if item["ok"])
    return (
        f"CODEX-A3-PLAT status={result['status']} "
        f"targets={sum(1 for name in TARGETS if (PLAT / name).is_file())}/{len(TARGETS)} "
        f"checks={passed}/{total} csv_rows={result['csv_rows']} "
        f"markdown={result['markdown_count']} yaml={'present' if result['yaml_present'] else 'missing'}"
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
            mark = "OK" if check["ok"] else "FAIL"
            print(f"{mark} {check['name']}: {check['detail']}")
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
