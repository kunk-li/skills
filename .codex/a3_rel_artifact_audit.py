#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


CHAIN_ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN")
REL_DIR = CHAIN_ROOT / "REL"

TARGETS = [
    "发布说明.md",
    "发版检查清单.csv",
    "变更摘要.md",
    "回滚预案.md",
    "灰度发布建议.md",
    "发布风险评估.md",
    "配置变更检查单.csv",
    "环境差异检查单.csv",
    "发布任务编排表.csv",
    "发布后验证清单.csv",
    "上线验收记录.md",
]

COMMON_REQUIRED = [
    "A3-ORG-REL-PILOT-001",
    "v0.1.0-target-BLOCKED",
    "oa-a3-org",
]

BLOCKERS = ["PEND-A3-02", "PEND-A3-03", "BRISK-002", "BRISK-006"]

NO_GO_REQUIRED = {
    "发布说明.md": ["NO_GO", "BLOCKED"],
    "发布风险评估.md": ["NO_GO", "BLOCKED", "go_no_go_recommendation"],
    "灰度发布建议.md": ["NO_CANARY", "BLOCKED"],
    "发布任务编排表.csv": ["circuit_breaker", "OPEN"],
    "发布后验证清单.csv": ["P0_completion_pct: 0"],
    "上线验收记录.md": ["ga_decision: NO_GO", "NOT_DEPLOYED"],
    "REL-COMPLETION-AUDIT.md": ["NO_GO", "BLOCKED"],
}


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
        raise ValueError("missing CSV data rows")
    return rows


def audit() -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    stats = {"targets": 0, "csv_rows": 0}

    if not REL_DIR.exists():
        return [f"missing REL dir: {REL_DIR.as_posix()}"], stats

    for name in TARGETS:
        path = REL_DIR / name
        if not path.exists():
            errors.append(f"missing target: {path.as_posix()}")
            continue
        stats["targets"] += 1
        text = read_text(path)
        for token in COMMON_REQUIRED:
            if token not in text:
                errors.append(f"{name}: missing common token {token}")
        if "TODO" in text or "UnsupportedOperationException" in text or "scaffold stub" in text:
            errors.append(f"{name}: contains forbidden placeholder token")
        if name.endswith(".csv"):
            try:
                rows = parse_csv_ignoring_comments(path)
                stats["csv_rows"] += len(rows)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{name}: CSV parse failed: {exc}")

    all_rel_text = "\n".join(read_text(path) for path in REL_DIR.glob("*") if path.is_file())
    for blocker in BLOCKERS:
        if blocker not in all_rel_text:
            errors.append(f"REL: missing blocker inheritance {blocker}")

    for name, tokens in NO_GO_REQUIRED.items():
        path = REL_DIR / name
        if not path.exists():
            errors.append(f"missing no-go artifact: {path.as_posix()}")
            continue
        text = read_text(path)
        for token in tokens:
            if token not in text:
                errors.append(f"{name}: missing no-go token {token}")

    rel_audit = REL_DIR / "REL-COMPLETION-AUDIT.md"
    if rel_audit.exists():
        audit_text = read_text(rel_audit)
        for name in TARGETS:
            if name not in audit_text:
                errors.append(f"REL-COMPLETION-AUDIT.md: missing target listing {name}")
    else:
        errors.append(f"missing completion audit: {rel_audit.as_posix()}")

    return errors, stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()

    errors, stats = audit()
    status = "pass" if not errors else "fail"
    summary = f"CODEX-A3-REL status={status} targets={stats['targets']}/{len(TARGETS)} csv_rows={stats['csv_rows']}"
    print(summary)
    if errors and not args.summary_line:
        for err in errors:
            print(f"ERROR {err}", file=sys.stderr)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
