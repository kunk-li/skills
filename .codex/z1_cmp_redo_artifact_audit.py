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

CHAIN_ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-Z1-watchdog/CHAIN")
REDO_ROOT = CHAIN_ROOT / "CMP-REDO"
TARGETS = ["FEATURE-LEVEL-CMP.csv", "CORE-FLOW-COUNT.json", "CMP-REDO-SUMMARY.md"]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def read(rel: str) -> str:
    return (REDO_ROOT / rel).read_text(encoding="utf-8")


def cmp_gate_audit() -> tuple[list[str], dict[str, object]]:
    gate_path = Path(__file__).resolve().with_name("cmp_method_gate.py")
    spec = importlib.util.spec_from_file_location("cmp_method_gate", gate_path)
    if spec is None or spec.loader is None:
        return [f"cannot load {gate_path}"], {}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module.audit(CHAIN_ROOT, "Z1-watchdog", 19)  # type: ignore[attr-defined]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()

    checks: list[Check] = []
    for rel in TARGETS:
        path = REDO_ROOT / rel
        checks.append(Check(f"file:CMP-REDO/{rel}", path.exists() and bool(read(rel).strip()) if path.exists() else False, rel))

    gate_errors, gate_stats = cmp_gate_audit()
    checks.append(Check("method:feature-level-full-non-sampling", not gate_errors, ";".join(gate_errors) if gate_errors else "D-102 gate"))

    summary = read("CMP-REDO-SUMMARY.md") if (REDO_ROOT / "CMP-REDO-SUMMARY.md").exists() else ""
    checks.append(
        Check(
            "legacy-cmp-invalid-recorded",
            "quick CMP pass" in summary and "COMPARE-FEATURE-MATRIX.csv" in summary,
            "old six-row quick CMP is retained only as invalid historical evidence",
        )
    )

    failed = [c for c in checks if not c.ok]
    print(
        "CODEX-Z1-CMP-REDO "
        f"status={'pass' if not failed else 'fail'} "
        f"targets={sum(1 for c in checks[:len(TARGETS)] if c.ok)}/{len(TARGETS)} "
        f"features={gate_stats.get('features', 0)}/19 "
        f"generated_full={gate_stats.get('generated_full', 0)} "
        f"generated_weighted={gate_stats.get('generated_weighted', 0)} "
        f"team_full={gate_stats.get('team_full', 0)} "
        f"team_weighted={gate_stats.get('team_weighted', 0)} "
        f"skill_gaps={gate_stats.get('skill_gaps', 0)} "
        f"checks={len(checks)-len(failed)}/{len(checks)} "
        f"failed={','.join(c.name for c in failed) if failed else '-'}"
    )
    if failed and not args.summary_line:
        for c in failed:
            print(f"FAIL {c.name}: {c.detail}", file=sys.stderr)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
