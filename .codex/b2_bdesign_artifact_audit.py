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

ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-B2-approval/CHAIN/B-design")


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def as_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


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
    "开发需求解析.md",
    "接口意图清单.md",
    "接口意图清单.csv",
    "技术方案分析.md",
    "技术方案初稿.md",
    "方案评审问题清单.md",
    "模块边界分析.md",
    "服务拆分建议.md",
    "接口设计草案.yaml",
    "API规范检查单.md",
    "API规范检查单.csv",
    "错误码清单.csv",
    "表结构设计草案.md",
    "索引设计建议.md",
    "数据流映射.md",
    "并发控制建议.md",
    "幂等设计建议.md",
    "审计留痕方案.md",
    "权限模型设计.md",
    "性能风险分析.md",
    "安全风险分析.md",
    "B-design-FINDINGS.md",
]


def build_checks() -> list[Check]:
    checks: list[Check] = [file_check(rel) for rel in TARGETS]
    checks.extend(
        [
            token_check("开发需求解析.md", ["ER-B2-001", "ER-B2-012", "问题点", "问题出现所在位置"]),
            token_check("接口意图清单.csv", ["API-B2-001", "API-B2-020", "totp", "idempotency"]),
            token_check("技术方案分析.md", ["FMEA-B2-001", "DEC-B2-004", "No fold decision"]),
            token_check("技术方案初稿.md", ["ApprovalStateMachine", "ApprovalAuditService", "BAR-EVAL remains pending"]),
            token_check("方案评审问题清单.md", ["RQ-B2-001", "RQ-B2-006", "Regression point for OA test"]),
            token_check("模块边界分析.md", ["B2 Approval", "hub-wflow", "D4 Employee Lifecycle", "J1 Audit"]),
            token_check("服务拆分建议.md", ["keep_modular_monolith", "Do not split B2"]),
            token_check("接口设计草案.yaml", ["/approval/ticket/{ticketId}/approve", "totpProof", "X-Current-Post-Org-Id"]),
            token_check("API规范检查单.md", ["gate_result: fail", "API-GATE-B2-002", "API-GATE-B2-008"]),
            token_check("API规范检查单.csv", ["API-GATE-B2-003", "fail", "Transfer"]),
            token_check("错误码清单.csv", ["WORK_CONTEXT_SWITCH_REQUIRED", "TOTP_REQUIRED_OR_INVALID", "AUDIT_CHAIN_VERIFY_FAILED"]),
            token_check("表结构设计草案.md", ["oa_approval_ticket", "oa_approval_sign_record", "oa_approval_idempotency"]),
            token_check("索引设计建议.md", ["IDX-B2-001", "IDX-B2-012"]),
            token_check("数据流映射.md", ["FLOW-B2-001", "FLOW-B2-010", "same proof/idempotency/audit path"]),
            token_check("并发控制建议.md", ["CON-B2-001", "CON-B2-008", "expectedVersion"]),
            token_check("幂等设计建议.md", ["IDEMPOTENCY_CONFLICT", "command_hash"]),
            token_check("审计留痕方案.md", ["AUD-B2-001", "AUD-B2-011", "hash-chain"]),
            token_check("权限模型设计.md", ["WORK_CONTEXT_SWITCH_REQUIRED", "participant-based plus current-post-context ABAC"]),
            token_check("性能风险分析.md", ["PERF-B2-001", "PERF-B2-007"]),
            token_check("安全风险分析.md", ["SEC-B2-001", "SEC-B2-009", "STRIDE"]),
            token_check("B-design-FINDINGS.md", ["B-design first pass is complete", "N150 API gate is intentionally `fail`", "No skill fold decision"]),
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
    api_gate = "fail" if "gate_result: fail" in read("API规范检查单.md") else "unknown"
    summary = (
        "CODEX-B2-BDESIGN "
        f"status={'pass' if not failed else 'fail'} "
        f"targets={target_passed}/{len(TARGETS)} "
        f"checks={len(checks) - len(failed)}/{len(checks)} "
        f"api_gate={api_gate} "
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
