#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


CHAIN_ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN")
OPS_DIR = CHAIN_ROOT / "OPS"

TARGETS = [
    "监控指标解读.md",
    "日志分析.md",
    "Trace分析.md",
    "Bug分析.md",
    "异常聚类表.csv",
    "高频报错摘要.md",
    "根因定位建议.md",
    "影响范围分析.md",
    "告警归因.md",
    "值班处置建议.md",
    "修复方案建议.md",
    "热修复风险评估.md",
    "故障时间线.md",
    "线上问题复盘.md",
]

COMMON_REQUIRED = [
    "A3-ORG-OPS-20260727-001",
    "A3-ORG-REL-PILOT-001",
    "oa-a3-org",
]

BLOCKERS = ["PEND-A3-02", "PEND-A3-03", "BRISK-002", "BRISK-006"]

HONESTY_TOKENS = [
    "NOT_DEPLOYED",
    "NO_GO",
]

FORBIDDEN_CLAIMS = [
    "已生产上线",
    "真实生产监控显示",
    "真实线上指标",
    "MTTR:",
    "MTTD:",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def parse_csv_ignoring_comments(path: Path) -> list[dict[str, str]]:
    lines = [line for line in read_text(path).splitlines() if line.strip() and not line.startswith("#")]
    if not lines:
        raise ValueError("no non-comment CSV content")
    reader = csv.DictReader(lines)
    rows = list(reader)
    if not reader.fieldnames:
        raise ValueError("missing CSV header")
    if not rows:
        raise ValueError("missing CSV rows")
    return rows


def audit() -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    stats = {"targets": 0, "csv_rows": 0}

    if not OPS_DIR.exists():
        return [f"missing OPS dir: {OPS_DIR.as_posix()}"], stats

    for name in TARGETS:
        path = OPS_DIR / name
        if not path.exists():
            errors.append(f"missing target: {path.as_posix()}")
            continue
        stats["targets"] += 1
        text = read_text(path)
        for token in COMMON_REQUIRED:
            if token not in text:
                errors.append(f"{name}: missing common token {token}")
        if name.endswith(".csv"):
            try:
                rows = parse_csv_ignoring_comments(path)
                stats["csv_rows"] += len(rows)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{name}: CSV parse failed: {exc}")
        if "TODO" in text or "UnsupportedOperationException" in text or "scaffold stub" in text:
            errors.append(f"{name}: contains forbidden placeholder token")
        for forbidden in FORBIDDEN_CLAIMS:
            if forbidden in text:
                errors.append(f"{name}: contains forbidden deployed claim {forbidden}")

    all_ops_text = "\n".join(read_text(path) for path in OPS_DIR.glob("*") if path.is_file())
    for blocker in BLOCKERS:
        if blocker not in all_ops_text:
            errors.append(f"OPS: missing blocker inheritance {blocker}")
    for token in HONESTY_TOKENS:
        if token not in all_ops_text:
            errors.append(f"OPS: missing honesty token {token}")

    completion = OPS_DIR / "OPS-COMPLETION-AUDIT.md"
    if not completion.exists():
        errors.append(f"missing completion audit: {completion.as_posix()}")
    else:
        text = read_text(completion)
        for name in TARGETS:
            if name not in text:
                errors.append(f"OPS-COMPLETION-AUDIT.md: missing target listing {name}")
        for token in ["NOT_DEPLOYED", "NO_GO"]:
            if token not in text:
                errors.append(f"OPS-COMPLETION-AUDIT.md: missing {token}")

    return errors, stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()

    errors, stats = audit()
    status = "pass" if not errors else "fail"
    print(f"CODEX-A3-OPS status={status} targets={stats['targets']}/{len(TARGETS)} csv_rows={stats['csv_rows']}")
    if errors and not args.summary_line:
        for err in errors:
            print(f"ERROR {err}", file=sys.stderr)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
