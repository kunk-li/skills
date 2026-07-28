#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / ".codex"
DEFAULT_STATE = CODEX / "oa_module_state.json"
DEFAULT_RULES = CODEX / "oa_bar_rules.json"
DEFAULT_REPORT_DIR = CODEX / "reports"
AUDIT_LOCK_PATH = CODEX / "tmp" / "oa_shakedown_audits.lock"
ALLOWED_CHAIN_ROOT = Path("D:/projects/skills-pilot")
CANONICAL_A3_CHAIN = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN")
BAD_A3_CHAIN = ROOT / "oaval-A3-org" / "CHAIN"

PASS_STATUSES = {"pass", "passed", "ok", "green", "done", "complete", "✅"}
PENDING_STATUSES = {"", "pending", "not_run", "not-done", "not_done", "todo", "unknown"}


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    hard: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "ok": self.ok, "hard": self.hard, "detail": self.detail}


class AuditLock:
    def __init__(self, path: Path, timeout: float = 240.0) -> None:
        self.path = path
        self.timeout = timeout
        self.handle: Any = None

    def __enter__(self) -> "AuditLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+b")
        deadline = time.time() + self.timeout
        if os.name == "nt":
            import msvcrt

            while True:
                try:
                    self.handle.seek(0)
                    msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
                    return self
                except OSError:
                    if time.time() >= deadline:
                        raise TimeoutError(f"timed out waiting for audit lock {as_posix(self.path)}")
                    time.sleep(0.5)
        else:
            import fcntl

            while True:
                try:
                    fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    return self
                except BlockingIOError:
                    if time.time() >= deadline:
                        raise TimeoutError(f"timed out waiting for audit lock {as_posix(self.path)}")
                    time.sleep(0.5)

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if not self.handle:
            return
        if os.name == "nt":
            import msvcrt

            self.handle.seek(0)
            try:
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            finally:
                self.handle.close()
        else:
            import fcntl

            try:
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            finally:
                self.handle.close()


def as_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def load_json(path: Path, name: str) -> tuple[dict[str, Any], Check]:
    if not path.exists():
        return {}, Check(name, False, f"missing {as_posix(path)}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {}, Check(name, False, f"invalid JSON in {as_posix(path)}: {exc}")
    if not isinstance(data, dict):
        return {}, Check(name, False, f"{as_posix(path)} must contain a JSON object")
    return data, Check(name, True, as_posix(path))


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(parent.resolve(strict=False))
        return True
    except Exception:
        lhs = as_posix(path.resolve(strict=False)).lower().rstrip("/")
        rhs = as_posix(parent.resolve(strict=False)).lower().rstrip("/")
        return lhs == rhs or lhs.startswith(rhs + "/")


def list_value(state: dict[str, Any], key: str) -> list[str]:
    value = state.get(key, [])
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def state_field_checks(state: dict[str, Any]) -> list[Check]:
    required = [
        "schema_version",
        "module_id",
        "total_status",
        "work_unit",
        "next",
        "bar_eval",
        "chain_root",
        "completed_phases",
        "pending_phases",
    ]
    checks: list[Check] = []
    for key in required:
        value = state.get(key)
        if key == "pending_phases":
            ok = isinstance(value, list)
        else:
            ok = value not in (None, "", [], {})
        checks.append(Check(f"state-field:{key}", ok, str(value)))

    completed = set(list_value(state, "completed_phases"))
    pending = set(list_value(state, "pending_phases"))
    overlap = sorted(completed & pending)
    checks.append(Check("phase-overlap", not overlap, "-" if not overlap else ",".join(overlap)))

    total_status = str(state.get("total_status", ""))
    checks.append(
        Check(
            "total-status-explicit",
            total_status in {"NOT_DONE", "PASS", "DONE", "NO_GO", "NOT_DEPLOYED", "BLOCKED"},
            total_status,
        )
    )
    return checks


def chain_checks(state: dict[str, Any]) -> list[Check]:
    chain = Path(str(state.get("chain_root", "")))
    module_id = str(state.get("module_id", ""))
    checks = [
        Check("chain-root-exists", chain.exists(), as_posix(chain)),
        Check("chain-root-under-skills-pilot", is_under(chain, ALLOWED_CHAIN_ROOT), as_posix(chain)),
    ]
    if module_id == "A3-org":
        checks.append(Check("a3-canonical-chain", chain.resolve(strict=False) == CANONICAL_A3_CHAIN.resolve(strict=False), as_posix(chain)))
        checks.append(Check("bad-root-a3-chain-absent", not BAD_A3_CHAIN.exists(), as_posix(BAD_A3_CHAIN)))
    return checks


def artifact_checks(state: dict[str, Any]) -> list[Check]:
    chain = Path(str(state.get("chain_root", "")))
    checks: list[Check] = []
    for rel in list_value(state, "required_artifacts"):
        path = chain / rel
        checks.append(Check(f"artifact:{rel}", path.exists(), as_posix(path)))
    return checks


def path_from_state(value: Any) -> Path:
    text = str(value or "")
    return Path(text) if text else Path()


def oracle_scope_checks(state: dict[str, Any]) -> list[Check]:
    """Keep validation-oracle evidence out of the normal production input contract."""

    addendum = state.get("full_code_addendum")
    if not isinstance(addendum, dict) or not addendum:
        return []

    checks: list[Check] = []
    scope = str(addendum.get("evidence_scope", ""))
    checks.append(Check("oracle-scope-declared", scope == "shakedown_oracle_only", scope or "missing"))

    production_allowed = addendum.get("production_input_allowed")
    checks.append(
        Check(
            "oracle-production-input-disallowed",
            production_allowed is False,
            str(production_allowed),
        )
    )

    unavailable = str(addendum.get("normal_production_availability", ""))
    checks.append(
        Check(
            "oracle-normal-production-unavailable",
            unavailable == "not_available",
            unavailable or "missing",
        )
    )

    bars = {str(item) for item in addendum.get("bars_not_satisfied_by_oracle", []) if str(item)}
    required_bars = {"bar1", "bar2", "bar5", "bar11"}
    checks.append(
        Check(
            "oracle-does-not-satisfy-production-bars",
            required_bars.issubset(bars),
            ",".join(sorted(bars)) or "missing",
        )
    )

    docs = {
        "oracle-team-decisions-doc": path_from_state(addendum.get("team_decisions")),
        "oracle-package-doc": path_from_state(addendum.get("package_doc")),
        "oracle-cmp-addendum-doc": path_from_state(addendum.get("cmp_addendum")),
        "oracle-bar-addendum-doc": path_from_state(addendum.get("bar_addendum")),
    }
    for name, path in docs.items():
        if not str(path):
            checks.append(Check(name, False, "missing path"))
            continue
        if not path.exists():
            checks.append(Check(name, False, as_posix(path)))
            continue
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        has_scope = "shakedown_oracle_only" in text
        has_boundary = "normal production" in text and "not available" in text
        checks.append(Check(name, has_scope and has_boundary, as_posix(path)))

    return checks


def rules_checks(rules: dict[str, Any]) -> list[Check]:
    bars = rules.get("bars", [])
    checks = [Check("bar-rules-count", isinstance(bars, list) and len(bars) == 11, str(len(bars) if isinstance(bars, list) else "not-list"))]
    if isinstance(bars, list):
        ids = [str(item.get("id", "")) for item in bars if isinstance(item, dict)]
        nums = [str(item.get("number", "")) for item in bars if isinstance(item, dict)]
        checks.append(Check("bar-rules-ids", ids == [f"bar{i}" for i in range(1, 12)], ",".join(ids)))
        checks.append(Check("bar-rules-numbers", nums == [str(i) for i in range(1, 12)], ",".join(nums)))
    return checks


def run_audit_script(name: str, script: Path) -> Check:
    if not script.exists():
        return Check(f"audit:{name}", False, f"missing {as_posix(script)}")
    try:
        proc = subprocess.run(
            [sys.executable, str(script), "--summary-line"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
    except Exception as exc:  # noqa: BLE001
        return Check(f"audit:{name}", False, str(exc))
    output = (proc.stdout or proc.stderr or "").strip()
    ok = proc.returncode == 0 and "status=pass" in output
    return Check(f"audit:{name}", ok, output)


def audit_checks(state: dict[str, Any], run_audits: bool) -> list[Check]:
    scripts = state.get("audit_scripts", {})
    if scripts in (None, {}):
        return []
    if not isinstance(scripts, dict):
        return [Check("audit-scripts-shape", False, "audit_scripts must be an object")]
    checks = [Check("audit-scripts-shape", True, f"{len(scripts)} scripts")]
    for name, script_value in scripts.items():
        script = Path(str(script_value))
        if run_audits:
            checks.append(run_audit_script(str(name), script))
        else:
            checks.append(Check(f"audit-script:{name}", script.exists(), as_posix(script)))
    return checks


def scorecard_candidates(state: dict[str, Any], suffix: str) -> list[Path]:
    chain = Path(str(state.get("chain_root", "")))
    configured = state.get("bar_eval_artifacts", {})
    candidates: list[Path] = []
    if isinstance(configured, dict):
        for value in configured.values():
            text = str(value)
            if text.lower().endswith(suffix):
                candidates.append(chain / text)
    candidates.extend(
        [
            chain / "BAR-EVAL" / f"BAR-EVAL-11BAR-SCORECARD{suffix}",
            chain / "BAR-EVAL" / f"11BAR-SCORECARD{suffix}",
            chain / "BAR-EVAL" / f"{state.get('module_id', 'MODULE')}-11BAR-SCORECARD{suffix}",
        ]
    )
    seen: set[str] = set()
    unique: list[Path] = []
    for path in candidates:
        key = as_posix(path)
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def normalize_bar_status(value: Any) -> str:
    text = str(value or "").strip().lower()
    return text


def parse_scorecard_json(path: Path) -> tuple[list[dict[str, Any]], str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [], f"invalid scorecard JSON: {exc}"
    raw = data.get("bars", data.get("scorecard", data if isinstance(data, list) else [])) if isinstance(data, dict) else data
    if not isinstance(raw, list):
        return [], "scorecard JSON must contain bars[] or be a list"
    bars: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        number = item.get("number", item.get("bar", item.get("id", "")))
        match = re.search(r"(\d+)", str(number))
        if not match:
            continue
        bars.append({"number": int(match.group(1)), "status": normalize_bar_status(item.get("status", item.get("verdict", ""))), "raw": item})
    return bars, None


def evaluate_bars(state: dict[str, Any], rules: dict[str, Any]) -> dict[str, Any]:
    total = len(rules.get("bars", [])) if isinstance(rules.get("bars"), list) else 0
    bar_eval_state = normalize_bar_status(state.get("bar_eval", "pending"))
    pending_phases = set(list_value(state, "pending_phases"))
    json_paths = scorecard_candidates(state, ".json")
    md_paths = scorecard_candidates(state, ".md")
    existing_json = next((path for path in json_paths if path.exists()), None)
    existing_md = next((path for path in md_paths if path.exists()), None)

    if bar_eval_state in PENDING_STATUSES or "BAR-EVAL" in pending_phases:
        return {
            "status": "pending",
            "passed": 0,
            "total": total,
            "all_pass": False,
            "blockers": ["BAR-EVAL_PENDING"],
            "scorecard_json": as_posix(existing_json) if existing_json else "",
            "scorecard_md": as_posix(existing_md) if existing_md else "",
            "detail": "BAR-EVAL has not produced the 11-bar scorecard yet.",
        }

    if not existing_json:
        return {
            "status": "missing_scorecard",
            "passed": 0,
            "total": total,
            "all_pass": False,
            "blockers": ["BAR_EVAL_SCORECARD_JSON_MISSING"],
            "scorecard_json": "",
            "scorecard_md": as_posix(existing_md) if existing_md else "",
            "detail": "bar_eval is not pending, but no machine-readable scorecard JSON was found.",
        }

    bars, error = parse_scorecard_json(existing_json)
    if error:
        return {
            "status": "invalid_scorecard",
            "passed": 0,
            "total": total,
            "all_pass": False,
            "blockers": ["BAR_EVAL_SCORECARD_INVALID"],
            "scorecard_json": as_posix(existing_json),
            "scorecard_md": as_posix(existing_md) if existing_md else "",
            "detail": error,
        }

    by_number = {item["number"]: item for item in bars}
    missing = [i for i in range(1, 12) if i not in by_number]
    passed = sum(1 for i in range(1, 12) if by_number.get(i, {}).get("status") in PASS_STATUSES)
    all_pass = not missing and passed == 11
    blockers = [] if all_pass else ["BAR_EVAL_NOT_ALL_PASS"]
    if missing:
        blockers.append("BAR_EVAL_MISSING_BARS:" + ",".join(str(i) for i in missing))
    return {
        "status": "pass" if all_pass else "not_pass",
        "passed": passed,
        "total": total,
        "all_pass": all_pass,
        "blockers": blockers,
        "scorecard_json": as_posix(existing_json),
        "scorecard_md": as_posix(existing_md) if existing_md else "",
        "detail": f"{passed}/11 bars pass",
    }


def computed_total(state: dict[str, Any], bar_eval: dict[str, Any]) -> str:
    pending = list_value(state, "pending_phases")
    if bar_eval.get("all_pass") and not pending:
        return "PASS"
    if not pending and bar_eval.get("status") != "pending":
        return "NO_GO"
    return "NOT_DONE"


def total_invariant_checks(state: dict[str, Any], computed: str, bar_eval: dict[str, Any]) -> list[Check]:
    state_total = str(state.get("total_status", ""))
    checks: list[Check] = []
    if state_total in {"PASS", "DONE"} and computed != "PASS":
        checks.append(Check("total-claim-requires-11-bars", False, f"state={state_total}, computed={computed}, blockers={bar_eval.get('blockers', [])}"))
    else:
        checks.append(Check("total-claim-requires-11-bars", True, f"state={state_total}, computed={computed}"))
    return checks


def build_report(
    state_path: Path = DEFAULT_STATE,
    rules_path: Path = DEFAULT_RULES,
    run_audits: bool = False,
    write_ledger: bool = False,
) -> dict[str, Any]:
    state, state_check = load_json(state_path, "state-json")
    rules, rules_check = load_json(rules_path, "bar-rules-json")
    checks = [state_check, rules_check]
    if state:
        checks.extend(state_field_checks(state))
        checks.extend(chain_checks(state))
        checks.extend(artifact_checks(state))
        checks.extend(oracle_scope_checks(state))
        if run_audits:
            try:
                with AuditLock(AUDIT_LOCK_PATH):
                    checks.extend(audit_checks(state, run_audits))
            except Exception as exc:  # noqa: BLE001
                checks.append(Check("audit-lock", False, str(exc)))
        else:
            checks.extend(audit_checks(state, run_audits))
    if rules:
        checks.extend(rules_checks(rules))

    bar_eval = evaluate_bars(state, rules) if state and rules else {
        "status": "unknown",
        "passed": 0,
        "total": 0,
        "all_pass": False,
        "blockers": ["STATE_OR_RULES_MISSING"],
        "detail": "state or rules missing",
    }
    computed = computed_total(state, bar_eval) if state else "NOT_DONE"
    if state:
        checks.extend(total_invariant_checks(state, computed, bar_eval))

    hard_failures = [check for check in checks if check.hard and not check.ok]
    report: dict[str, Any] = {
        "schema_version": "codex.oa_shakedown_report.v1",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "run_status": "pass" if not hard_failures else "fail",
        "state_path": as_posix(state_path),
        "rules_path": as_posix(rules_path),
        "module": state.get("module_id", "UNKNOWN"),
        "module_label": state.get("module_label", ""),
        "state_total": state.get("total_status", "UNKNOWN"),
        "computed_total": computed,
        "work_unit": state.get("work_unit", "UNKNOWN"),
        "next": state.get("next", "UNKNOWN"),
        "chain_root": state.get("chain_root", ""),
        "completed_phases": list_value(state, "completed_phases"),
        "pending_phases": list_value(state, "pending_phases"),
        "bar_eval": bar_eval,
        "checks": [check.to_dict() for check in checks],
    }
    if write_ledger:
        report["ledger_paths"] = write_ledgers(report)
    return report


def check_counts(report: dict[str, Any]) -> tuple[int, int, str]:
    checks = report.get("checks", [])
    total = len(checks)
    passed = sum(1 for item in checks if item.get("ok"))
    failed = ",".join(str(item.get("name")) for item in checks if not item.get("ok")) or "-"
    return passed, total, failed


def module_gate_summary(report: dict[str, Any]) -> str:
    passed, total, failed = check_counts(report)
    return (
        f"CODEX-OA-MODULE-GATE status={report['run_status']} "
        f"module={report['module']} total={report['state_total']} computed_total={report['computed_total']} "
        f"work_unit={report['work_unit']} next={report['next']} "
        f"completed={len(report.get('completed_phases', []))} pending={len(report.get('pending_phases', []))} "
        f"bar_eval={report.get('bar_eval', {}).get('status', 'unknown')} checks={passed}/{total} failed={failed}"
    )


def shakedown_summary(report: dict[str, Any]) -> str:
    passed, total, failed = check_counts(report)
    bars = report.get("bar_eval", {})
    blockers = ",".join(bars.get("blockers", [])) or "-"
    return (
        f"CODEX-OA-SHAKEDOWN run={report['run_status']} "
        f"module={report['module']} state_total={report['state_total']} computed_total={report['computed_total']} "
        f"work_unit={report['work_unit']} next={report['next']} "
        f"phases_done={len(report.get('completed_phases', []))} phases_pending={len(report.get('pending_phases', []))} "
        f"bars={bars.get('passed', 0)}/{bars.get('total', 0)} bar_eval={bars.get('status', 'unknown')} "
        f"blockers={blockers} checks={passed}/{total} failed={failed}"
    )


def markdown_report(report: dict[str, Any]) -> str:
    bars = report.get("bar_eval", {})
    lines = [
        "# OA Shakedown Report",
        "",
        f"- Module: `{report['module']}`",
        f"- State total: `{report['state_total']}`",
        f"- Computed total: `{report['computed_total']}`",
        f"- Work unit: `{report['work_unit']}`",
        f"- Next: `{report['next']}`",
        f"- Chain root: `{report['chain_root']}`",
        f"- State file: `{report['state_path']}`",
        f"- Bar rules: `{report['rules_path']}`",
        "",
        "## Phase State",
        "",
        f"- Completed: {', '.join(report.get('completed_phases', [])) or '-'}",
        f"- Pending: {', '.join(report.get('pending_phases', [])) or '-'}",
        "",
        "## Bar Eval",
        "",
        f"- Status: `{bars.get('status', 'unknown')}`",
        f"- Passed: `{bars.get('passed', 0)}/{bars.get('total', 0)}`",
        f"- Blockers: `{', '.join(bars.get('blockers', [])) or '-'}`",
        f"- Detail: {bars.get('detail', '-')}",
        "",
        "## Checks",
        "",
    ]
    for item in report.get("checks", []):
        mark = "OK" if item.get("ok") else "FAIL"
        lines.append(f"- {mark} `{item.get('name')}`: {item.get('detail')}")
    lines.append("")
    lines.append(shakedown_summary(report))
    return "\n".join(lines)


def write_ledgers(report: dict[str, Any]) -> dict[str, str]:
    DEFAULT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    module = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(report.get("module", "module"))).strip("-") or "module"
    stem = f"{now_stamp()}-{module}-oa-shakedown"
    json_path = DEFAULT_REPORT_DIR / f"{stem}.json"
    md_path = DEFAULT_REPORT_DIR / f"{stem}.md"
    latest_json = DEFAULT_REPORT_DIR / "oa_shakedown_latest.json"
    latest_md = DEFAULT_REPORT_DIR / "oa_shakedown_latest.md"
    json_text = json.dumps(report, ensure_ascii=False, indent=2)
    md_text = markdown_report(report)
    json_path.write_text(json_text + "\n", encoding="utf-8")
    md_path.write_text(md_text + "\n", encoding="utf-8")
    latest_json.write_text(json_text + "\n", encoding="utf-8")
    latest_md.write_text(md_text + "\n", encoding="utf-8")
    return {
        "json": as_posix(json_path),
        "markdown": as_posix(md_path),
        "latest_json": as_posix(latest_json),
        "latest_markdown": as_posix(latest_md),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default=str(DEFAULT_STATE))
    parser.add_argument("--rules", default=str(DEFAULT_RULES))
    parser.add_argument("--run-audits", action="store_true")
    parser.add_argument("--write-ledger", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--summary-line", action="store_true")
    parser.add_argument("--module-gate-summary", action="store_true")
    parser.add_argument("--assert-run-pass", action="store_true")
    parser.add_argument("--assert-total-pass", action="store_true")
    args = parser.parse_args()

    report = build_report(Path(args.state), Path(args.rules), run_audits=args.run_audits, write_ledger=args.write_ledger)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.module_gate_summary:
        print(module_gate_summary(report))
    elif args.summary_line:
        print(shakedown_summary(report))
    else:
        print(shakedown_summary(report))
        if "ledger_paths" in report:
            for key, value in report["ledger_paths"].items():
                print(f"{key}: {value}")

    if args.assert_run_pass and report["run_status"] != "pass":
        return 2
    if args.assert_total_pass and report["computed_total"] != "PASS":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
