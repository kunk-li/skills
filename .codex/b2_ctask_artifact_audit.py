#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-B2-approval/CHAIN/C-task")


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def as_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def file_check(rel: str) -> Check:
    path = ROOT / rel
    if not path.exists():
        return Check(f"file:{rel}", False, f"missing {as_posix(path)}")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return Check(f"file:{rel}", False, f"utf8_decode_failed {exc}")
    if not text.strip():
        return Check(f"file:{rel}", False, f"empty {as_posix(path)}")
    return Check(f"file:{rel}", True, f"{len(text.splitlines())} lines")


def token_check(rel: str, tokens: list[str]) -> Check:
    path = ROOT / rel
    if not path.exists():
        return Check(f"tokens:{rel}", False, f"missing {as_posix(path)}")
    text = path.read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in text]
    if missing:
        return Check(f"tokens:{rel}", False, "missing tokens: " + " | ".join(missing))
    return Check(f"tokens:{rel}", True, "required tokens present")


TARGETS = [
    "开发任务拆分表.md",
    "开发任务拆分表.csv",
    "工时估算表.md",
    "工时估算表.csv",
    "研发依赖清单.md",
    "研发依赖清单.csv",
    "N180_planning_package.md",
]


def build_checks() -> list[Check]:
    checks = [file_check(rel) for rel in TARGETS]
    checks.extend(
        [
            token_check("开发任务拆分表.md", ["Total tasks: 34", "TASK-B2-001", "TASK-B2-034", "044 API gate fail"]),
            token_check("开发任务拆分表.csv", ["TASK-B2-001", "TASK-B2-034", "no fold until A/B evidence"]),
            token_check("工时估算表.md", ["Total", "94.3", "API gate fail"]),
            token_check("工时估算表.csv", ["Total,34,50.0,88.0,164.0,94.3"]),
            token_check("研发依赖清单.md", ["DEP-B2-001", "Critical Path", "Blocked Until Decision"]),
            token_check("研发依赖清单.csv", ["DEP-B2-010", "CMP dimensions require implementation surface"]),
            token_check("N180_planning_package.md", ["constrained", "D-code may start only as guarded reference implementation", "current post context"]),
        ]
    )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()
    checks = build_checks()
    failed = [check for check in checks if not check.ok]
    target_passed = sum(1 for check in checks[: len(TARGETS)] if check.ok)
    summary = (
        "CODEX-B2-CTASK "
        f"status={'pass' if not failed else 'fail'} "
        f"targets={target_passed}/{len(TARGETS)} "
        f"checks={len(checks) - len(failed)}/{len(checks)} "
        f"failed={','.join(check.name for check in failed) if failed else '-'}"
    )
    if args.summary_line:
        print(summary)
    else:
        print(summary)
        for check in checks:
            print(("PASS" if check.ok else "FAIL") + f" {check.name}: {check.detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
