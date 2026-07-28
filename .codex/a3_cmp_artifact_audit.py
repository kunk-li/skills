#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


CHAIN_ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN")
CMP_DIR = CHAIN_ROOT / "CMP"

TARGETS = [
    "CMP-SUMMARY.md",
    "FEATURE-CMP-MATRIX.csv",
    "API-ENDPOINT-CMP.csv",
    "GENERATED-INVENTORY.csv",
    "TEAM-INVENTORY.csv",
    "CODE-METRICS.json",
    "OBSERVATION-FOR-OA-VERIFY.md",
    "CMP-COMPLETION-AUDIT.md",
]

REQUIRED_TOKENS = [
    "A3-ORG-CMP-20260727-001",
    "A3-ORG-REL-PILOT-001",
    "oa-a3-org",
    "NO_GO",
    "NOT_DEPLOYED",
    "not_globally_generated_gte_team",
]

BLOCKERS = ["PEND-A3-02", "PEND-A3-03", "BRISK-002", "BRISK-006"]

FORBIDDEN_CLAIMS = [
    "已生产上线",
    "真实生产监控显示",
    "已有正式 OA 签核",
    "generated >= team 全局通过",
    "generated≥team 全局通过",
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
        raise ValueError("missing header")
    if not rows:
        raise ValueError("missing rows")
    return rows


def audit() -> tuple[list[str], dict[str, int | str]]:
    errors: list[str] = []
    stats: dict[str, int | str] = {
        "targets": 0,
        "feature_rows": 0,
        "endpoint_rows": 0,
        "generated_java": 0,
        "team_java": 0,
        "verdict": "missing",
    }

    if not CMP_DIR.exists():
        return [f"missing CMP dir: {CMP_DIR.as_posix()}"], stats

    texts: list[str] = []
    for name in TARGETS:
        path = CMP_DIR / name
        if not path.exists():
            errors.append(f"missing target: {path.as_posix()}")
            continue
        stats["targets"] = int(stats["targets"]) + 1
        text = read_text(path)
        texts.append(text)
        for forbidden in FORBIDDEN_CLAIMS:
            if forbidden in text:
                errors.append(f"{name}: contains forbidden claim {forbidden}")
        if name.endswith(".csv"):
            try:
                rows = parse_csv_ignoring_comments(path)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{name}: CSV parse failed: {exc}")
                continue
            if name == "FEATURE-CMP-MATRIX.csv":
                stats["feature_rows"] = len(rows)
                required_cols = {"cmp_id", "domain", "generated_status", "team_status", "verdict", "generated_evidence", "team_evidence"}
                missing = required_cols - set(rows[0])
                if missing:
                    errors.append(f"{name}: missing columns {sorted(missing)}")
                if len(rows) != 20:
                    errors.append(f"{name}: expected 20 feature rows, got {len(rows)}")
                verdicts = {row.get("verdict", "") for row in rows}
                for expected in [
                    "generated_stronger_on_boundary_safety",
                    "generated_core_matches_team_after_repair",
                    "generated_core_matches_team_lock_baseline_after_repair",
                    "not_globally_generated_gte_team",
                ]:
                    if expected not in verdicts:
                        errors.append(f"{name}: missing verdict {expected}")
                for row in rows:
                    if row.get("generated_evidence") == "not_found" or row.get("team_evidence") == "not_found":
                        errors.append(f"{name}: evidence not_found for {row.get('cmp_id')}")
            elif name == "API-ENDPOINT-CMP.csv":
                stats["endpoint_rows"] = len(rows)
                sides = {row.get("side") for row in rows}
                if not {"generated", "team"}.issubset(sides):
                    errors.append(f"{name}: must include generated and team endpoints")
            elif name == "GENERATED-INVENTORY.csv":
                stats["generated_java"] = len(rows)
            elif name == "TEAM-INVENTORY.csv":
                stats["team_java"] = len(rows)
        if name == "CODE-METRICS.json":
            try:
                metrics = json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f"{name}: JSON parse failed: {exc}")
            else:
                stats["verdict"] = metrics.get("global_verdict", "missing")
                if metrics.get("global_verdict") != "not_globally_generated_gte_team":
                    errors.append(f"{name}: unexpected global_verdict {metrics.get('global_verdict')}")
                if metrics.get("feature_rows") != 20:
                    errors.append(f"{name}: feature_rows must be 20")
                if int(metrics.get("generated", {}).get("java_files", 0)) <= 0:
                    errors.append(f"{name}: generated java count missing")
                if int(metrics.get("team", {}).get("java_files", 0)) <= 0:
                    errors.append(f"{name}: team java count missing")

    joined = "\n".join(texts)
    for token in REQUIRED_TOKENS + BLOCKERS:
        if token not in joined:
            errors.append(f"CMP: missing required token {token}")

    completion = CMP_DIR / "CMP-COMPLETION-AUDIT.md"
    if completion.exists():
        completion_text = read_text(completion)
        for name in TARGETS:
            if name == "CMP-COMPLETION-AUDIT.md":
                continue
            if name not in completion_text:
                errors.append(f"CMP-COMPLETION-AUDIT.md: missing target listing {name}")
    return errors, stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()

    errors, stats = audit()
    status = "pass" if not errors else "fail"
    print(
        "CODEX-A3-CMP "
        f"status={status} "
        f"targets={stats['targets']}/{len(TARGETS)} "
        f"features={stats['feature_rows']} "
        f"endpoints={stats['endpoint_rows']} "
        f"generated_java={stats['generated_java']} "
        f"team_java={stats['team_java']} "
        f"verdict={stats['verdict']}"
    )
    if errors and not args.summary_line:
        for err in errors:
            print(f"ERROR {err}", file=sys.stderr)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
