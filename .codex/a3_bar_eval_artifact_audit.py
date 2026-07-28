#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Codex-owned audit for A3 BAR-EVAL artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

CHAIN = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN")
BAR_EVAL = CHAIN / "BAR-EVAL"
TARGETS = [
    "BAR-EVAL-11BAR-SCORECARD.json",
    "BAR-EVAL-11BAR-SCORECARD.md",
    "BAR-EVAL-COMPLETION-AUDIT.md",
    "BAR-EVAL-ARTIFACT-MANIFEST.json",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_scorecard() -> tuple[dict[str, Any], str | None]:
    path = BAR_EVAL / "BAR-EVAL-11BAR-SCORECARD.json"
    if not path.exists():
        return {}, "missing scorecard"
    try:
        data = json.loads(read_text(path))
    except Exception as exc:  # noqa: BLE001
        return {}, str(exc)
    return data if isinstance(data, dict) else {}, None


def audit() -> dict[str, Any]:
    checks: list[dict[str, Any]] = [{"name": "bar-eval-dir", "ok": BAR_EVAL.is_dir(), "detail": str(BAR_EVAL)}]
    for name in TARGETS:
        path = BAR_EVAL / name
        checks.append({"name": f"target:{name}", "ok": path.is_file(), "detail": str(path)})

    scorecard, error = load_scorecard()
    pass_count = partial_count = fail_count = 0
    verdict = "UNKNOWN"
    if error:
        checks.append({"name": "scorecard-json", "ok": False, "detail": error})
    else:
        bars = scorecard.get("bars", [])
        verdict = str(scorecard.get("total_verdict", "UNKNOWN"))
        checks.append({"name": "bars-count", "ok": isinstance(bars, list) and len(bars) == 11, "detail": str(len(bars) if isinstance(bars, list) else "not-list")})
        if isinstance(bars, list):
            numbers = sorted(int(item.get("number", -1)) for item in bars if isinstance(item, dict))
            checks.append({"name": "bars-numbered-1-11", "ok": numbers == list(range(1, 12)), "detail": ",".join(str(item) for item in numbers)})
            pass_count = sum(1 for item in bars if isinstance(item, dict) and item.get("status") == "PASS")
            partial_count = sum(1 for item in bars if isinstance(item, dict) and item.get("status") == "PARTIAL")
            fail_count = sum(1 for item in bars if isinstance(item, dict) and item.get("status") == "FAIL")
        checks.append({"name": "verdict-no-go", "ok": verdict == "NO_GO", "detail": verdict})
        checks.append({"name": "not-all-pass", "ok": scorecard.get("all_pass") is False and pass_count < 11, "detail": f"{pass_count}/11"})

    md_path = BAR_EVAL / "BAR-EVAL-11BAR-SCORECARD.md"
    if md_path.exists():
        text = read_text(md_path)
        checks.append({"name": "md-verdict-no-go", "ok": "Total verdict: NO_GO" in text, "detail": md_path.name})
        checks.append({"name": "md-cmp-evidence-only", "ok": "CMP is code-comparison evidence only" in text, "detail": md_path.name})

    audit_path = BAR_EVAL / "BAR-EVAL-COMPLETION-AUDIT.md"
    if audit_path.exists():
        text = read_text(audit_path)
        checks.append({"name": "audit-computed-total-no-go", "ok": "computed_total must be NO_GO" in text, "detail": audit_path.name})

    manifest_path = BAR_EVAL / "BAR-EVAL-ARTIFACT-MANIFEST.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(read_text(manifest_path))
            checks.append({"name": "manifest-verdict", "ok": manifest.get("total_verdict") == "NO_GO", "detail": str(manifest.get("total_verdict"))})
        except Exception as exc:  # noqa: BLE001
            checks.append({"name": "manifest-json", "ok": False, "detail": str(exc)})

    ok = all(item["ok"] for item in checks)
    return {
        "module": "A3-org",
        "status": "pass" if ok else "blocked",
        "targets": TARGETS,
        "checks": checks,
        "pass_count": pass_count,
        "partial_count": partial_count,
        "fail_count": fail_count,
        "verdict": verdict,
    }


def summary(result: dict[str, Any]) -> str:
    total = len(result["checks"])
    passed = sum(1 for item in result["checks"] if item["ok"])
    existing = sum(1 for name in TARGETS if (BAR_EVAL / name).is_file())
    return (
        f"CODEX-A3-BAR-EVAL status={result['status']} "
        f"targets={existing}/{len(TARGETS)} checks={passed}/{total} "
        f"bars={result['pass_count']}/11 partial={result['partial_count']} "
        f"fail={result['fail_count']} verdict={result['verdict']}"
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
            print(f"{'OK' if check['ok'] else 'FAIL'} {check['name']}: {check['detail']}")
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
