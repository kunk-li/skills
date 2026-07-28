#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

CHAIN_ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-B2-approval/CHAIN")
LEGACY_ROOT = CHAIN_ROOT / "CMP"
REDO_ROOT = CHAIN_ROOT / "CMP-REDO"
TARGETS = ["FEATURE-LEVEL-CMP.csv", "CORE-FLOW-COUNT.json", "CMP-REDO-SUMMARY.md"]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def t(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def cmp_gate_audit() -> tuple[list[str], dict[str, object]]:
    gate_path = Path(__file__).resolve().with_name("cmp_method_gate.py")
    spec = importlib.util.spec_from_file_location("cmp_method_gate", gate_path)
    if spec is None or spec.loader is None:
        return [f"cannot load {gate_path}"], {}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module.audit(CHAIN_ROOT, "B2-approval", 15)  # type: ignore[attr-defined]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()
    checks = []
    for rel in TARGETS:
        path = REDO_ROOT / rel
        checks.append(Check(f"file:CMP-REDO/{rel}", path.exists() and bool(t(REDO_ROOT, rel).strip()) if path.exists() else False, rel))

    gate_errors, gate_stats = cmp_gate_audit()
    checks.append(Check("method:feature-level-full-non-sampling", not gate_errors, ";".join(gate_errors) if gate_errors else "D-102 gate"))

    legacy_matrix = LEGACY_ROOT / "COMPARE-MATRIX.csv"
    legacy_text = legacy_matrix.read_text(encoding="utf-8", errors="replace") if legacy_matrix.exists() else ""
    checks.append(
        Check(
            "legacy-cmp-invalid-recorded",
            "sampled_team_code" in legacy_text and "CMP-B2-012" in legacy_text and "sampled_team_code" in t(REDO_ROOT, "CMP-REDO-SUMMARY.md"),
            "old CMP is retained only as invalid historical evidence",
        )
    )
    failed = [c for c in checks if not c.ok]
    features = gate_stats.get("features", 0)
    generated_full = gate_stats.get("generated_full", 0)
    generated_weighted = gate_stats.get("generated_weighted", 0)
    team_full = gate_stats.get("team_full", 0)
    team_weighted = gate_stats.get("team_weighted", 0)
    skill_gaps = gate_stats.get("skill_gaps", 0)
    summary = (
        "CODEX-B2-CMP "
        f"status={'pass' if not failed else 'fail'} "
        f"targets={sum(1 for c in checks[:len(TARGETS)] if c.ok)}/{len(TARGETS)} "
        f"features={features}/15 "
        f"generated_full={generated_full} "
        f"generated_weighted={generated_weighted} "
        f"team_full={team_full} "
        f"team_weighted={team_weighted} "
        f"skill_gaps={skill_gaps} "
        f"checks={len(checks)-len(failed)}/{len(checks)} "
        "verdict=cmp_redo_no_generated_gte_team "
        f"failed={','.join(c.name for c in failed) if failed else '-'}"
    )
    print(summary)
    if not args.summary_line:
        for c in checks:
            print(("PASS" if c.ok else "FAIL") + f" {c.name}: {c.detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
