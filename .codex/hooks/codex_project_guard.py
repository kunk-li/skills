#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
CODEX_DIR = ROOT / ".codex"
MEMORY_PATH = CODEX_DIR / "MEMORY.md"
sys.path.insert(0, str(CODEX_DIR))

from oa_shakedown import DEFAULT_RULES, DEFAULT_STATE, as_posix, build_report, module_gate_summary  # noqa: E402
from utf8_io import scan_controlled_files  # noqa: E402

PRIVATE_SURFACE_TOKEN = "." + "cla" + "ude"
FORBIDDEN_WRAPPER_TOKENS = [
    PRIVATE_SURFACE_TOKEN,
    "load_" + "memory.py",
    "stop_" + "check.py",
]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    hard: bool = True


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_rules() -> dict[str, Any]:
    try:
        return json.loads(DEFAULT_RULES.read_text(encoding="utf-8"))
    except Exception:
        return {}


def required_doc_tokens(report: dict[str, Any]) -> dict[Path, list[str]]:
    state_tokens = [
        f"OA_MODULE_ID={report['module']}",
        f"OA_MODULE_TOTAL={report['state_total']}",
        f"OA_MODULE_WORK_UNIT={report['work_unit']}",
        f"OA_MODULE_NEXT={report['next']}",
        "11 条验收 bar",
        "不是总判定",
        "BAR-EVAL",
        str(report.get("chain_root", "")),
    ]
    rules = load_rules()
    bar_labels = []
    for item in rules.get("bars", []):
        if isinstance(item, dict) and item.get("label"):
            bar_labels.append(str(item["label"]))
    return {
        ROOT / "STATUS.md": state_tokens,
        ROOT / "TOOL-HARDENING-PLAN.md": state_tokens,
        ROOT / "DECISIONS.md": ["D-060", "D-133", "D-134", "11 条验收 bar", *bar_labels],
        MEMORY_PATH: [
            "Durable Memory",
            "_sessions/` is audit history only",
            "PowerShell text pipelines",
            "utf8_io.py scan",
            "Do not hardcode A3",
            "CMP is code-comparison evidence only",
            "BAR-EVAL over D-060's 11 bars is the total judgment",
            "A3 is fully walked but not passed",
            "Daily reports are content-first",
        ],
    }


def check_required_text(path: Path, tokens: list[str]) -> Check:
    if not path.exists():
        return Check(f"text:{path.name}", False, f"missing file: {as_posix(path)}")
    try:
        content = read_text(path)
    except Exception as exc:  # noqa: BLE001
        return Check(f"text:{path.name}", False, f"cannot read {as_posix(path)}: {exc}")
    missing = [token for token in tokens if token not in content]
    if missing:
        return Check(f"text:{path.name}", False, "missing tokens: " + " | ".join(missing))
    return Check(f"text:{path.name}", True, "required tokens present")


def check_native_hooks() -> Check:
    hook_files = [
        CODEX_DIR / "hooks" / "session_start_context.py",
        CODEX_DIR / "hooks" / "stop_ritual_check.py",
        CODEX_DIR / "hooks" / "skill_chain_gate.py",
        CODEX_DIR / "hooks" / "codex_project_guard.py",
    ]
    failures: list[str] = []
    for path in hook_files:
        if not path.exists():
            failures.append(f"missing {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        hits = [token for token in FORBIDDEN_WRAPPER_TOKENS if token in text]
        if hits:
            failures.append(f"{path.name} contains private-surface wrapper token")
    if failures:
        return Check("codex-native-hooks", False, "; ".join(failures))
    return Check("codex-native-hooks", True, "Codex hooks are native and do not forward to other tool-private surfaces")


def check_hooks_registered() -> Check:
    hooks_path = CODEX_DIR / "hooks.json"
    if not hooks_path.exists():
        return Check("hooks-registered", False, f"missing {as_posix(hooks_path)}")
    try:
        text = hooks_path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        return Check("hooks-registered", False, f"cannot read hooks.json: {exc}")
    needed = ["codex_project_guard.py", "skill_chain_gate.py", "UserPromptSubmit", "Stop"]
    missing = [token for token in needed if token not in text]
    if missing:
        return Check("hooks-registered", False, "missing hook tokens: " + " | ".join(missing))
    return Check("hooks-registered", True, "Codex guard and module gate are registered in hooks.json")


def check_session_start_memory() -> Check:
    path = CODEX_DIR / "hooks" / "session_start_context.py"
    if not path.exists():
        return Check("session-start-memory", False, f"missing {as_posix(path)}")
    text = path.read_text(encoding="utf-8")
    needed = ["MEMORY_PATH", "Codex Durable Memory", "Latest Session Pointer"]
    missing = [token for token in needed if token not in text]
    if missing:
        return Check("session-start-memory", False, "missing tokens: " + " | ".join(missing))
    if "# Latest Session - `" in text:
        return Check("session-start-memory", False, "session_start_context still injects latest session body")
    return Check("session-start-memory", True, "startup context loads durable memory and keeps sessions as pointers")


def check_utf8_guard() -> Check:
    findings = scan_controlled_files()
    if findings:
        detail = "; ".join(
            f"{as_posix(item.path)} pattern={item.pattern.encode('unicode_escape').decode('ascii')} count={item.count}"
            for item in findings[:8]
        )
        return Check("utf8-controlled-files", False, detail)
    return Check("utf8-controlled-files", True, "controlled Codex/project text files decode as UTF-8 with no known mojibake markers")


def check_completion_closure_guard() -> Check:
    path = CODEX_DIR / "completion_closure_guard.py"
    if not path.exists():
        return Check("completion-closure-selftest", False, f"missing {as_posix(path)}")
    proc = subprocess.run(
        [sys.executable, str(path), "--self-test", "--summary-line"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = " ".join((proc.stdout + "\n" + proc.stderr).split())
    ok = proc.returncode == 0 and "status=pass" in output
    return Check("completion-closure-selftest", ok, output or f"exit={proc.returncode}")


def run_checks() -> list[Check]:
    report = build_report()
    checks: list[Check] = [
        Check("oa-shakedown-invariants", report["run_status"] == "pass", module_gate_summary(report)),
        Check("oa-state-file", DEFAULT_STATE.exists(), as_posix(DEFAULT_STATE)),
        Check("oa-bar-rules", DEFAULT_RULES.exists(), as_posix(DEFAULT_RULES)),
    ]
    for path, tokens in required_doc_tokens(report).items():
        checks.append(check_required_text(path, tokens))
    checks.append(check_native_hooks())
    checks.append(check_session_start_memory())
    checks.append(check_utf8_guard())
    checks.append(check_completion_closure_guard())
    checks.append(check_hooks_registered())
    return checks


def status_payload(checks: list[Check]) -> dict[str, Any]:
    hard_failures = [item for item in checks if not item.ok and item.hard]
    soft_failures = [item for item in checks if not item.ok and not item.hard]
    return {
        "status": "pass" if not hard_failures else "fail",
        "root": as_posix(ROOT),
        "checks": [
            {
                "name": item.name,
                "ok": item.ok,
                "hard": item.hard,
                "detail": item.detail,
            }
            for item in checks
        ],
        "hard_failures": len(hard_failures),
        "soft_failures": len(soft_failures),
    }


def summary_line(payload: dict[str, Any]) -> str:
    total = len(payload["checks"])
    passed = sum(1 for item in payload["checks"] if item["ok"])
    failed_names = ",".join(item["name"] for item in payload["checks"] if not item["ok"]) or "-"
    return (
        f"CODEX-PROJECT-GUARD status={payload['status']} "
        f"checks={passed}/{total} hard_failures={payload['hard_failures']} "
        f"failed={failed_names}"
    )


def emit_hook(payload: dict[str, Any], event_name: str) -> None:
    failures = [item for item in payload["checks"] if not item["ok"]]
    if failures:
        reason = "; ".join(f"{item['name']}: {item['detail']}" for item in failures[:8])
        output = {
            "systemMessage": f"Codex project guard failed: {reason}",
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": (
                    "Codex project guard found a hard project-discipline failure.\n"
                    "Fix this before answering as if the project state is valid.\n\n"
                    f"{summary_line(payload)}\n"
                    f"{reason}\n\n"
                    "Current rules: module state lives in `D:/work/资料/skills/.codex/oa_module_state.json`; "
                    "the 11-bar rules live in `D:/work/资料/skills/.codex/oa_bar_rules.json`; "
                    "BAR-EVAL is the total judgment; CMP and phase audits are evidence only."
                ),
            },
        }
    else:
        output = {
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": (
                    f"{summary_line(payload)}\n"
                    "Codex project guard passed. Module state is driven by "
                    "`D:/work/资料/skills/.codex/oa_module_state.json`; "
                    "BAR-EVAL over the 11 bars is the total judgment; CMP and phase audits are evidence only."
                ),
            }
        }
    json.dump(output, sys.stdout, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--summary-line", action="store_true")
    parser.add_argument("--hook", choices=["UserPromptSubmit", "Stop"])
    args = parser.parse_args()

    payload = status_payload(run_checks())
    if args.json:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        print()
    elif args.summary_line:
        print(summary_line(payload))
    elif args.hook:
        emit_hook(payload, args.hook)
    else:
        print(summary_line(payload))
        for check in payload["checks"]:
            mark = "OK" if check["ok"] else "FAIL"
            print(f"{mark} {check['name']}: {check['detail']}")
    return 0 if payload["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
