#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

REQUIRED_COLUMNS = [
    "feature_id",
    "module",
    "core_business_feature",
    "prd_anchor",
    "generated_true_flow_status",
    "generated_core_realization",
    "generated_code_evidence",
    "generated_runtime_boundary",
    "team_true_flow_status",
    "team_core_realization",
    "team_code_evidence",
    "team_runtime_boundary",
    "business_usable_delta",
    "gap_attribution_5class",
    "skill_gap",
    "skill_gap_candidate",
    "notes",
]

ALLOWED_STATUSES = {"full", "partial", "missing", "stub", "owner_external", "prd_blocked"}
ALLOWED_REALIZATION = {"0", "0.5", "1"}
ALLOWED_ATTRIBUTIONS = {
    "NONE",
    "A1_PRD_DECISION_GAP",
    "A2_OWNER_BOUNDARY",
    "A3_TRUE_BLIND_SPOT",
    "A4_GENERATION_STOPPED",
    "A5_SCAFFOLD_FAIL_OPEN",
}
SKILL_GAP_ATTRIBUTIONS = {"A3_TRUE_BLIND_SPOT", "A4_GENERATION_STOPPED", "A5_SCAFFOLD_FAIL_OPEN"}
FORBIDDEN_METHOD_TOKENS = [
    "sampled_team_code",
    "quick cmp",
    "quick_cmp",
    "sampling_pass",
    "dimension,generated_reference",
]


def as_posix(path: Path) -> str:
    return str(path).replace("\\", "/")


def read_csv(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(text.splitlines())
    return list(reader)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def split_attr(value: str) -> set[str]:
    return {part.strip() for part in value.split("|") if part.strip()}


def yes(value: str) -> bool:
    return value.strip().lower() in {"yes", "true", "1"}


def num(value: str) -> float:
    return float(value.strip())


def audit(chain_root: Path, module: str, expected_features: int) -> tuple[list[str], dict[str, Any]]:
    cmp_dir = chain_root / "CMP-REDO"
    matrix = cmp_dir / "FEATURE-LEVEL-CMP.csv"
    counts_path = cmp_dir / "CORE-FLOW-COUNT.json"
    summary = cmp_dir / "CMP-REDO-SUMMARY.md"

    errors: list[str] = []
    stats: dict[str, Any] = {
        "module": module,
        "targets": 0,
        "features": 0,
        "generated_full": 0,
        "generated_weighted": 0.0,
        "team_full": 0,
        "team_weighted": 0.0,
        "skill_gaps": 0,
    }

    for path in [matrix, counts_path, summary]:
        if path.exists() and path.read_text(encoding="utf-8", errors="replace").strip():
            stats["targets"] += 1
        else:
            errors.append(f"missing or empty target: {as_posix(path)}")

    if not matrix.exists():
        return errors, stats

    raw_matrix_text = matrix.read_text(encoding="utf-8", errors="replace")
    lowered = raw_matrix_text.lower()
    for token in FORBIDDEN_METHOD_TOKENS:
        if token in lowered:
            errors.append(f"forbidden sampling token in matrix: {token}")

    try:
        rows = read_csv(matrix)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"matrix csv parse failed: {exc}")
        return errors, stats

    stats["features"] = len(rows)
    if len(rows) != expected_features:
        errors.append(f"expected {expected_features} feature rows, got {len(rows)}")
    if rows:
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in rows[0]]
        if missing_cols:
            errors.append(f"matrix missing columns: {missing_cols}")

    seen: set[str] = set()
    for idx, row in enumerate(rows, start=2):
        fid = row.get("feature_id", "").strip()
        if not fid:
            errors.append(f"row {idx}: missing feature_id")
        if fid in seen:
            errors.append(f"row {idx}: duplicate feature_id {fid}")
        seen.add(fid)
        if row.get("module", "").strip() != module:
            errors.append(f"row {idx}: module must be {module}")

        for side in ["generated", "team"]:
            status = row.get(f"{side}_true_flow_status", "").strip()
            if status not in ALLOWED_STATUSES:
                errors.append(f"row {idx}: invalid {side}_true_flow_status {status}")
            realization = row.get(f"{side}_core_realization", "").strip()
            if realization not in ALLOWED_REALIZATION:
                errors.append(f"row {idx}: invalid {side}_core_realization {realization}")

        for col in ["generated_code_evidence", "team_code_evidence", "business_usable_delta"]:
            val = row.get(col, "").strip()
            if not val or val.lower() in {"not_found", "todo", "tbd", "待确认"}:
                errors.append(f"row {idx}: weak evidence in {col}")

        attrs = split_attr(row.get("gap_attribution_5class", ""))
        if not attrs:
            errors.append(f"row {idx}: missing gap attribution")
        unknown = attrs - ALLOWED_ATTRIBUTIONS
        if unknown:
            errors.append(f"row {idx}: invalid attribution {sorted(unknown)}")

        has_skill_gap = bool(attrs & SKILL_GAP_ATTRIBUTIONS)
        if yes(row.get("skill_gap", "")) != has_skill_gap:
            errors.append(f"row {idx}: skill_gap must match A3/A4/A5 attribution")
        if has_skill_gap and not row.get("skill_gap_candidate", "").strip():
            errors.append(f"row {idx}: skill gap row must name candidate")

    stats["generated_full"] = sum(1 for row in rows if row.get("generated_core_realization", "").strip() == "1")
    stats["team_full"] = sum(1 for row in rows if row.get("team_core_realization", "").strip() == "1")
    stats["generated_weighted"] = round(sum(num(row.get("generated_core_realization", "0")) for row in rows), 2)
    stats["team_weighted"] = round(sum(num(row.get("team_core_realization", "0")) for row in rows), 2)
    stats["skill_gaps"] = sum(1 for row in rows if yes(row.get("skill_gap", "")))

    if counts_path.exists():
        try:
            counts = read_json(counts_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"count json parse failed: {exc}")
        else:
            expected_pairs = {
                "feature_total": len(rows),
                "generated_realized_full": stats["generated_full"],
                "team_realized_full": stats["team_full"],
                "skill_gap_rows": stats["skill_gaps"],
            }
            for key, expected in expected_pairs.items():
                if counts.get(key) != expected:
                    errors.append(f"count json {key} expected {expected}, got {counts.get(key)}")
            for key in ["cmp_method", "team_code_scope", "production_skill_input_allowed"]:
                if key not in counts:
                    errors.append(f"count json missing {key}")
            if counts.get("cmp_method") != "feature_level_full_non_sampling":
                errors.append("count json cmp_method must be feature_level_full_non_sampling")
            if counts.get("team_code_scope") != "shakedown_oracle_only":
                errors.append("count json team_code_scope must be shakedown_oracle_only")
            if counts.get("production_skill_input_allowed") is not False:
                errors.append("count json production_skill_input_allowed must be false")

    if summary.exists():
        text = summary.read_text(encoding="utf-8", errors="replace")
        for token in [
            "cmp_method=feature_level_full_non_sampling",
            "team_code_scope=shakedown_oracle_only",
            "production_skill_input_allowed=false",
            "formal_skill_zip_changed=false",
        ]:
            if token not in text:
                errors.append(f"summary missing token {token}")

    return errors, stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", required=True)
    parser.add_argument("--chain-root", required=True)
    parser.add_argument("--expected-features", type=int, required=True)
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()

    errors, stats = audit(Path(args.chain_root), args.module, args.expected_features)
    status = "pass" if not errors else "fail"
    print(
        "CODEX-CMP-METHOD "
        f"status={status} "
        f"module={args.module} "
        f"targets={stats['targets']}/3 "
        f"features={stats['features']}/{args.expected_features} "
        f"generated_full={stats['generated_full']} "
        f"generated_weighted={stats['generated_weighted']} "
        f"team_full={stats['team_full']} "
        f"team_weighted={stats['team_weighted']} "
        f"skill_gaps={stats['skill_gaps']} "
        f"failed={','.join(errors) if errors else '-'}"
    )
    if errors and not args.summary_line:
        for err in errors:
            print(f"ERROR {err}", file=sys.stderr)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
