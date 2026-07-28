#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
import zipfile
from pathlib import Path


CHAIN_ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN")
DOC_DIR = CHAIN_ROOT / "DOC"

TARGETS = [
    "开发文档.md",
    "接口文档.md",
    "模块设计说明.md",
    "数据字典.xlsx",
    "部署文档.md",
    "维护手册.md",
    "行动项清单.csv",
    "周报.md",
    "FAQ.md",
    "最佳实践.md",
    "任务清单.csv",
    "任务状态同步.md",
    "阻塞项清单.csv",
    "风险项清单.csv",
    "产品研发对齐摘要.md",
    "测试研发对齐摘要.md",
    "版本范围裁剪建议.md",
    "项目节奏跟踪表.csv",
]

COMMON_REQUIRED = [
    "A3-ORG-DOC-20260727-001",
    "A3-ORG-REL-PILOT-001",
    "oa-a3-org",
    "NO_GO",
    "NOT_DEPLOYED",
]

BLOCKERS = ["PEND-A3-02", "PEND-A3-03", "BRISK-002", "BRISK-006"]

FORBIDDEN_CLAIMS = [
    "已生产上线",
    "真实生产监控显示",
    "真实线上指标",
    "已有正式 OA 签核",
    "已完成生产发布",
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


def read_xlsx_text(path: Path) -> str:
    if not zipfile.is_zipfile(path):
        raise ValueError("not a valid xlsx zip")
    parts: list[str] = []
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        required_parts = {"[Content_Types].xml", "xl/workbook.xml"}
        missing = sorted(required_parts - names)
        if missing:
            raise ValueError(f"missing xlsx parts: {', '.join(missing)}")
        for name in archive.namelist():
            if name.endswith(".xml") or name.endswith(".rels"):
                parts.append(archive.read(name).decode("utf-8", errors="ignore"))
    return "\n".join(parts)


def artifact_text(path: Path) -> str:
    if path.suffix.lower() == ".xlsx":
        return read_xlsx_text(path)
    return read_text(path)


def audit() -> tuple[list[str], dict[str, int | str]]:
    errors: list[str] = []
    stats: dict[str, int | str] = {"targets": 0, "csv_rows": 0, "workbook": "missing"}

    if not DOC_DIR.exists():
        return [f"missing DOC dir: {DOC_DIR.as_posix()}"], stats

    all_text: list[str] = []
    for name in TARGETS:
        path = DOC_DIR / name
        if not path.exists():
            errors.append(f"missing target: {path.as_posix()}")
            continue

        stats["targets"] = int(stats["targets"]) + 1
        try:
            text = artifact_text(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: read failed: {exc}")
            continue
        all_text.append(text)

        if path.suffix.lower() == ".xlsx":
            stats["workbook"] = "present"
        else:
            for token in COMMON_REQUIRED:
                if token not in text:
                    errors.append(f"{name}: missing common token {token}")

        if name.endswith(".csv"):
            try:
                rows = parse_csv_ignoring_comments(path)
                stats["csv_rows"] = int(stats["csv_rows"]) + len(rows)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{name}: CSV parse failed: {exc}")

        if "TODO" in text or "UnsupportedOperationException" in text or "scaffold stub" in text:
            errors.append(f"{name}: contains forbidden placeholder token")
        for forbidden in FORBIDDEN_CLAIMS:
            if forbidden in text:
                errors.append(f"{name}: contains forbidden deployed claim {forbidden}")

    joined = "\n".join(all_text)
    for token in COMMON_REQUIRED:
        if token not in joined:
            errors.append(f"DOC: missing shared required token {token}")
    for blocker in BLOCKERS:
        if blocker not in joined:
            errors.append(f"DOC: missing blocker inheritance {blocker}")

    completion = DOC_DIR / "DOC-COMPLETION-AUDIT.md"
    if not completion.exists():
        errors.append(f"missing completion audit: {completion.as_posix()}")
    else:
        completion_text = read_text(completion)
        for name in TARGETS:
            if name not in completion_text:
                errors.append(f"DOC-COMPLETION-AUDIT.md: missing target listing {name}")
        for token in COMMON_REQUIRED + BLOCKERS:
            if token not in completion_text:
                errors.append(f"DOC-COMPLETION-AUDIT.md: missing {token}")

    return errors, stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()

    errors, stats = audit()
    status = "pass" if not errors else "fail"
    print(
        "CODEX-A3-DOC "
        f"status={status} "
        f"targets={stats['targets']}/{len(TARGETS)} "
        f"csv_rows={stats['csv_rows']} "
        f"workbook={stats['workbook']}"
    )
    if errors and not args.summary_line:
        for err in errors:
            print(f"ERROR {err}", file=sys.stderr)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
