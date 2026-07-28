#!/usr/bin/env python3
"""Audit the N180 -> 060 implement handoff fold candidate."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGING_ROOT = Path("D:/projects/skills-pilot/_fold-n180-implement-handoff")

SOURCE_TOKEN_CHECKS = {
    STAGING_ROOT / "src/055/development-task-breakdown/SKILL.md": [
        "codegen_blocker_classification[]",
        "R13_no_whole_dcode_block_for_implementable_flows",
        "n190_handoff.060_selected_mode",
    ],
    STAGING_ROOT / "src/057/dependency-identification/SKILL.md": [
        "codegen_dependency_resolution[]",
        "R15_implementable_flows_force_060_implement",
        "downstream_handoff.N190",
    ],
    STAGING_ROOT / "src/060/service-draft-generation/SKILL.md": [
        "R_IMPL_N180_HANDOFF_CONSUMED",
        "downstream_handoff.N190.060_selected_mode=implement",
        "selected_mode=implement",
    ],
    STAGING_ROOT / "src/060/service-draft-generation/references/service-self-check.yaml": [
        "R_IMPL_N180_HANDOFF_CONSUMED",
        "guarded_reference_only",
        "true_owner_product_blocker",
    ],
}

ZIP_TOKEN_CHECKS = {
    REPO_ROOT / "\u5b8c\u7a3f/N180 \u7814\u53d1\u4efb\u52a1\u89c4\u5212/055-development-task-breakdown.zip": [
        "R13_no_whole_dcode_block_for_implementable_flows",
        "scripts/validate_codegen_handoff.py",
    ],
    REPO_ROOT / "\u5b8c\u7a3f/N180 \u7814\u53d1\u4efb\u52a1\u89c4\u5212/057-dependency-identification.zip": [
        "R15_implementable_flows_force_060_implement",
        "scripts/validate_codegen_handoff.py",
    ],
    REPO_ROOT / "\u5b8c\u7a3f/N190 \u4ee3\u7801\u9aa8\u67b6\u751f\u6210/060-service-draft-generation.zip": [
        "R_IMPL_N180_HANDOFF_CONSUMED",
        "n180_handoff_dispatch",
    ],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_tokens(errors: list[str], checks: dict[Path, list[str]], *, zipped: bool) -> int:
    passed = 0
    for path, tokens in checks.items():
        if not path.exists():
            errors.append(f"missing file: {path}")
            continue
        if zipped:
            with zipfile.ZipFile(path) as zf:
                names = zf.namelist()
                payload = "\n".join(names)
                for name in names:
                    if name.endswith((".md", ".yaml", ".yml", ".py")):
                        payload += "\n" + zf.read(name).decode("utf-8", errors="replace")
        else:
            payload = read_text(path)
        for token in tokens:
            if token not in payload:
                errors.append(f"token_missing: {path} :: {token}")
            else:
                passed += 1
    return passed


def run_validator(errors: list[str], script: Path, fixture: Path, expected_status: str) -> int:
    proc = subprocess.run(
        [sys.executable, str(script), str(fixture)],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        errors.append(f"validator_bad_json: {script} {fixture}: {proc.stdout!r} {proc.stderr!r}")
        return 0
    actual = payload.get("status")
    if actual != expected_status:
        errors.append(
            f"validator_status_mismatch: {script.name} {fixture.name} expected={expected_status} actual={actual}"
        )
        return 0
    if expected_status == "pass" and proc.returncode != 0:
        errors.append(f"validator_exit_mismatch: {script.name} {fixture.name} pass exit={proc.returncode}")
        return 0
    if expected_status == "fail" and proc.returncode == 0:
        errors.append(f"validator_exit_mismatch: {script.name} {fixture.name} fail exit=0")
        return 0
    return 1


def count_library_zips(errors: list[str]) -> int:
    total = len(list((REPO_ROOT / "\u5b8c\u7a3f").glob("**/*.zip")))
    if total != 157:
        errors.append(f"library_zip_count_expected_157_actual_{total}")
        return 0
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    parser.add_argument("--skip-zip", action="store_true", help="Skip checks that require repacked library zips.")
    args = parser.parse_args()

    errors: list[str] = []
    checks = 0
    checks += check_tokens(errors, SOURCE_TOKEN_CHECKS, zipped=False)

    fixture_bad = STAGING_ROOT / "fixtures/bad-b2-guarded-reference-handoff.json"
    fixture_good = STAGING_ROOT / "fixtures/good-b2-implement-handoff.json"
    checks += run_validator(
        errors,
        STAGING_ROOT / "src/055/development-task-breakdown/scripts/validate_codegen_handoff.py",
        fixture_bad,
        "fail",
    )
    checks += run_validator(
        errors,
        STAGING_ROOT / "src/055/development-task-breakdown/scripts/validate_codegen_handoff.py",
        fixture_good,
        "pass",
    )
    checks += run_validator(
        errors,
        STAGING_ROOT / "src/057/dependency-identification/scripts/validate_codegen_handoff.py",
        fixture_bad,
        "fail",
    )
    checks += run_validator(
        errors,
        STAGING_ROOT / "src/057/dependency-identification/scripts/validate_codegen_handoff.py",
        fixture_good,
        "pass",
    )

    if not args.skip_zip:
        checks += check_tokens(errors, ZIP_TOKEN_CHECKS, zipped=True)
        checks += count_library_zips(errors)

    status = "pass" if not errors else "fail"
    result = {
        "status": status,
        "checks": checks,
        "errors": errors,
    }
    if args.summary_line:
        failed = "-" if not errors else "|".join(errors)
        print(f"CODEX-N180-IMPLEMENT-HANDOFF status={status} checks={checks} failed={failed}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
