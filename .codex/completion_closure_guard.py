#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / ".codex"
STATUS_PATH = ROOT / "STATUS.md"

STANDARD_AUDITS = [
    ("feature-depth", CODEX / "feature_depth_batch_fold_audit.py", ["--summary-line"]),
    ("formal-genericity", CODEX / "formal_skill_genericity_audit.py", ["--summary-line"]),
    ("runtime-boundary", CODEX / "runtime_boundary_chain_fold_audit.py", ["--summary-line"]),
    ("self-contained-runtime", CODEX / "self_contained_runtime_fold_audit.py", ["--summary-line"]),
    ("standalone-production", CODEX / "b2_z1_standalone_production_audit.py", ["--summary-line"]),
    ("project-guard", CODEX / "hooks" / "codex_project_guard.py", ["--summary-line"]),
    ("utf8", CODEX / "utf8_io.py", ["scan", "--summary-line"]),
    ("oa-shakedown", CODEX / "oa_shakedown.py", ["--summary-line"]),
]

HANDOFF_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        r"下一步\s*(?:是|:|：)",
        r"要不要",
        r"是否继续",
        r"如果你想",
        r"你可以",
        r"需要你",
        r"等你",
        r"再告诉我",
        r"我可以继续",
    ]
]

BATCH_CLOSED_TERMS = ["当前批次已闭合", "当前批次闭合", "本批次已闭合", "本批次闭合", "本轮闭合"]
INTERNAL_QUEUE_TERMS = ["内部自动续跑队列", "不是用户待办", "不是让用户再下"]
NO_GO_TERMS = ["总判定仍 NO_GO", "总判定 NO_GO", "OA_MODULE_TOTAL=NO_GO", "11 条验收 bar 未全过"]
EXTERNAL_BLOCKER_TERMS = ["剩余外部阻塞", "外部 blocker", "外部 blockers", "外部阻塞"]


@dataclass
class AuditResult:
    name: str
    ok: bool
    detail: str


def as_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section_after_header(text: str, header: str) -> str:
    marker = f"## {header}"
    start = text.find(marker)
    if start < 0:
        return ""
    rest = text[start + len(marker) :]
    next_header = rest.find("\n## ")
    return rest if next_header < 0 else rest[:next_header]


def has_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def has_bad_handoff(text: str) -> bool:
    return any(pattern.search(text) for pattern in HANDOFF_PATTERNS)


def has_batch_closure(text: str) -> bool:
    return has_any(text, BATCH_CLOSED_TERMS) and has_any(text, INTERNAL_QUEUE_TERMS) and has_any(text, NO_GO_TERMS)


def has_external_blocker_closure(text: str) -> bool:
    return has_any(text, EXTERNAL_BLOCKER_TERMS) and has_any(text, NO_GO_TERMS)


def auto_queue_active(status_text: str) -> bool:
    queue = section_after_header(status_text, "自动续跑队列")
    if not queue:
        return False
    active_tokens = ["继续自动", "批量筛", "partial_after", "still_open", "fold / no_fold / deferred"]
    inactive_tokens = ["已清空", "无剩余", "NONE", "closed"]
    return has_any(queue, active_tokens) and not has_any(queue, inactive_tokens)


def status_has_user_next_step(status_text: str) -> bool:
    return "\n## 下一步" in status_text or status_text.startswith("## 下一步")


def classify(
    status_text: str,
    final_text: str | None,
    *,
    allow_current_batch_closed: bool,
    audits: list[AuditResult],
    audits_required: bool,
) -> dict[str, Any]:
    reasons: list[str] = []
    active_queue = auto_queue_active(status_text)
    next_step_header = status_has_user_next_step(status_text)
    final = final_text or ""
    final_present = final_text is not None
    batch_closure = has_batch_closure(final)
    blocker_closure = has_external_blocker_closure(final)
    bad_handoff = has_bad_handoff(final)

    if next_step_header:
        reasons.append("STATUS_HAS_USER_NEXT_STEP_SECTION")
    if bad_handoff and not (batch_closure or blocker_closure):
        reasons.append("FINAL_HANDS_OFF_NEXT_STEP")

    if active_queue:
        if not final_present:
            reasons.append("AUTO_QUEUE_ACTIVE_FINAL_TEXT_REQUIRED")
        elif not allow_current_batch_closed:
            reasons.append("AUTO_QUEUE_ACTIVE")
        elif not batch_closure:
            reasons.append("AUTO_QUEUE_ACTIVE_MISSING_BATCH_CLOSURE")

    failed_audits = [item for item in audits if not item.ok]
    if audits_required and failed_audits:
        reasons.append("AUDITS_FAILED")

    decision = "continue" if reasons else "complete"
    if decision == "complete" and blocker_closure:
        decision = "blocked"

    return {
        "schema_version": "codex.completion_closure_guard.v1",
        "decision": decision,
        "status": "continue" if decision == "continue" else decision,
        "root": as_posix(ROOT),
        "status_path": as_posix(STATUS_PATH),
        "auto_queue_active": active_queue,
        "status_has_user_next_step_section": next_step_header,
        "final_text_present": final_present,
        "final_bad_handoff": bad_handoff,
        "final_batch_closure": batch_closure,
        "final_external_blocker_closure": blocker_closure,
        "allow_current_batch_closed": allow_current_batch_closed,
        "audits_required": audits_required,
        "audits": [{"name": item.name, "ok": item.ok, "detail": item.detail} for item in audits],
        "reasons": reasons,
    }


def run_audit(name: str, script: Path, args: list[str], timeout: int) -> AuditResult:
    if not script.exists():
        return AuditResult(name, False, f"missing {as_posix(script)}")
    proc = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    output = " ".join((proc.stdout + "\n" + proc.stderr).split())
    ok = proc.returncode == 0 and "status=fail" not in output and "run=fail" not in output
    return AuditResult(name, ok, output[:600] or f"exit={proc.returncode}")


def run_audits(require_clean_audits: bool, timeout: int) -> list[AuditResult]:
    if not require_clean_audits:
        return []
    results: list[AuditResult] = []
    for name, script, args in STANDARD_AUDITS:
        try:
            results.append(run_audit(name, script, args, timeout))
        except Exception as exc:  # noqa: BLE001
            results.append(AuditResult(name, False, str(exc)))
    return results


def summary_line(payload: dict[str, Any]) -> str:
    audits = payload["audits"]
    if audits:
        audit_total = len(audits)
        audit_passed = sum(1 for item in audits if item["ok"])
        audit_text = f"{audit_passed}/{audit_total}"
        failed = ",".join(item["name"] for item in audits if not item["ok"]) or "-"
    else:
        audit_text = "skipped"
        failed = "-"
    reasons = ",".join(payload["reasons"]) or "-"
    return (
        f"CODEX-COMPLETION-CLOSURE status={payload['status']} "
        f"decision={payload['decision']} audits={audit_text} failed={failed} reasons={reasons}"
    )


def self_test_payload() -> dict[str, Any]:
    active_status = """
# Status

## 现在做什么

正在做支线。

## 自动续跑队列

这是内部队列,不是让用户再下“下一步”指令。继续自动批量筛 partial_after_OA2=10。
"""
    bad_status = """
# Status

## 下一步

继续让用户决定。
"""
    closed_final = "当前批次已闭合；剩余为内部自动续跑队列，不是用户待办；总判定仍 NO_GO。"
    bad_final = "下一步是继续筛缺口，要不要我继续？"
    checks = [
        (
            "active_queue_without_final_continues",
            classify(active_status, None, allow_current_batch_closed=False, audits=[], audits_required=False)["decision"] == "continue",
        ),
        (
            "active_queue_bad_final_continues",
            classify(active_status, bad_final, allow_current_batch_closed=True, audits=[], audits_required=False)["decision"] == "continue",
        ),
        (
            "active_queue_closed_final_completes",
            classify(active_status, closed_final, allow_current_batch_closed=True, audits=[], audits_required=False)["decision"] == "complete",
        ),
        (
            "user_next_step_status_continues",
            classify(bad_status, closed_final, allow_current_batch_closed=True, audits=[], audits_required=False)["decision"] == "continue",
        ),
        (
            "clean_no_queue_completes",
            classify("# Status\n\n## 现在做什么\n\n当前批次闭合。\n", "当前批次已闭合。", allow_current_batch_closed=False, audits=[], audits_required=False)["decision"] == "complete",
        ),
    ]
    failed = [name for name, ok in checks if not ok]
    return {
        "status": "pass" if not failed else "fail",
        "checks": [{"name": name, "ok": ok} for name, ok in checks],
        "failed": failed,
    }


def self_test_summary(payload: dict[str, Any]) -> str:
    checks = payload["checks"]
    passed = sum(1 for item in checks if item["ok"])
    failed = ",".join(payload["failed"]) or "-"
    return f"CODEX-COMPLETION-CLOSURE-SELFTEST status={payload['status']} checks={passed}/{len(checks)} failed={failed}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-final closure guard: complete, continue, or blocked.")
    parser.add_argument("--summary-line", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--final-text")
    parser.add_argument("--allow-current-batch-closed", action="store_true")
    parser.add_argument("--require-clean-audits", action="store_true")
    parser.add_argument("--audit-timeout", type=int, default=240)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        payload = self_test_payload()
        if args.json:
            json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
            print()
        else:
            print(self_test_summary(payload))
        return 0 if payload["status"] == "pass" else 2

    if not STATUS_PATH.exists():
        payload = {
            "schema_version": "codex.completion_closure_guard.v1",
            "decision": "continue",
            "status": "continue",
            "root": as_posix(ROOT),
            "status_path": as_posix(STATUS_PATH),
            "audits": [],
            "reasons": ["STATUS_MISSING"],
        }
    else:
        final_text = read_text(Path(args.final_text)) if args.final_text else None
        audits = run_audits(args.require_clean_audits, args.audit_timeout)
        payload = classify(
            read_text(STATUS_PATH),
            final_text,
            allow_current_batch_closed=args.allow_current_batch_closed,
            audits=audits,
            audits_required=args.require_clean_audits,
        )

    if args.json:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        print(summary_line(payload))

    return 2 if payload["decision"] == "continue" else 0


if __name__ == "__main__":
    raise SystemExit(main())
