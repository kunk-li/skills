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

ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-B2-approval/CHAIN")


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def as_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def file_check(rel: str) -> Check:
    path = ROOT / rel
    if not path.exists():
        return Check(f"file:{rel}", False, f"missing {as_posix(path)}")
    try:
        text = read(path)
    except UnicodeDecodeError as exc:
        return Check(f"file:{rel}", False, f"utf8_decode_failed {exc}")
    if not text.strip():
        return Check(f"file:{rel}", False, f"empty {as_posix(path)}")
    return Check(f"file:{rel}", True, f"{len(text.splitlines())} lines")


def token_check(rel: str, tokens: list[str]) -> Check:
    path = ROOT / rel
    if not path.exists():
        return Check(f"tokens:{rel}", False, f"missing {as_posix(path)}")
    text = read(path)
    missing = [token for token in tokens if token not in text]
    if missing:
        return Check(f"tokens:{rel}", False, "missing tokens: " + " | ".join(missing))
    return Check(f"tokens:{rel}", True, "required tokens present")


def build_checks() -> list[Check]:
    checks: list[Check] = []
    expected_files = [
        "00-input/SOURCE-PINS.md",
        "00-input/PRD-B2-approval-slice.md",
        "PARSE/需求结构拆解.md",
        "PARSE/业务规则清单.md",
        "PARSE/状态转移图.md",
        "PARSE/权限矩阵.md",
        "PARSE/数据对象目录.md",
        "PARSE/PRD评审问题清单.md",
        "PARSE/PARSE-FINDINGS.md",
    ]
    checks.extend(file_check(rel) for rel in expected_files)
    checks.append(
        token_check(
            "00-input/SOURCE-PINS.md",
            [
                "B2-approval",
                "9ffba18f2",
                "cd50ae2",
                "shakedown oracle evidence only",
                "read-only",
            ],
        )
    )
    checks.append(token_check("00-input/PRD-B2-approval-slice.md", ["PRD_B2_approval_v1.0", "TicketStatus"]))
    checks.append(token_check("PARSE/需求结构拆解.md", ["96", "TicketStatus", "dual-sign"]))
    checks.append(token_check("PARSE/业务规则清单.md", ["78", "RULE-B2-001", "RULE-B2-015"]))
    checks.append(token_check("PARSE/状态转移图.md", ["State machines: 8", "SM-B2-TICKET", "SM-B2-DUALSIGN"]))
    checks.append(token_check("PARSE/权限矩阵.md", ["Permission rows: 44", "WORK_CONTEXT_SWITCH_REQUIRED"]))
    checks.append(token_check("PARSE/数据对象目录.md", ["Objects: 18", "OaTicket", "OaApprovalTransferLog"]))
    checks.append(
        token_check(
            "PARSE/PRD评审问题清单.md",
            [
                "Q-B2-001",
                "Q-B2-006",
                "问题点",
                "问题出现所在位置",
                "Regression point for OA test",
            ],
        )
    )
    checks.append(
        token_check(
            "PARSE/PARSE-FINDINGS.md",
            [
                "B2-approval",
                "PARSE is complete",
                "问题点",
                "问题出现所在位置",
                "No skill fold decision is made at PARSE",
            ],
        )
    )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()

    checks = build_checks()
    failed = [check for check in checks if not check.ok]
    targets = 9
    present_targets = sum(1 for check in checks[:targets] if check.ok)
    summary = (
        "CODEX-B2-PARSE "
        f"status={'pass' if not failed else 'fail'} "
        f"targets={present_targets}/{targets} "
        f"checks={len(checks) - len(failed)}/{len(checks)} "
        f"failed={','.join(check.name for check in failed) if failed else '-'}"
    )
    if args.summary_line:
        print(summary)
    else:
        print(summary)
        for check in checks:
            mark = "PASS" if check.ok else "FAIL"
            print(f"{mark} {check.name}: {check.detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
