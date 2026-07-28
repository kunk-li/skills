#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parents[1]
FOLD_ROOT = Path(
    "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/"
    "b2-z1-standalone-production-code/FOLD-061-066-088-101-RUNTIME-BOUNDARY-CHAIN"
)
EXPECTED_LIBRARY_ZIPS = 157


def canonical_skill_zips() -> list[Path]:
    return [p for p in REPO.rglob("*.zip") if any(part == "完稿" for part in p.parts)]


def find_one(pattern: str) -> Path:
    matches = list(REPO.rglob(pattern))
    if len(matches) != 1:
        raise AssertionError(f"expected exactly one {pattern}, found {len(matches)}")
    return matches[0]


def read_zip_text(zip_path: Path, member: str) -> str:
    with zipfile.ZipFile(zip_path) as zf:
        return zf.read(member).decode("utf-8")


def extract_zip(zip_path: Path, dest: Path) -> Path:
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)
    roots = [p for p in dest.iterdir() if p.is_dir()]
    if len(roots) != 1:
        raise AssertionError(f"expected one root in {dest}, found {len(roots)}")
    return roots[0]


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def write_json(path: Path, doc: dict) -> Path:
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_text(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()

    checks: list[str] = []
    failed: list[str] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append(name)
        if not condition:
            failed.append(f"{name}{': ' + detail if detail else ''}")

    try:
        check("library_zip_count_157", len(canonical_skill_zips()) == EXPECTED_LIBRARY_ZIPS, str(len(canonical_skill_zips())))

        z061 = find_one("061-repository-draft-generation.zip")
        z066 = find_one("066-sql-draft-generation.zip")
        z088 = find_one("088-test-automation-orchestration.zip")
        z101 = find_one("101-release-checklist-generation.zip")

        pre088 = FOLD_ROOT / "088-test-automation-orchestration.zip.pre-runtime-boundary-chain.bak"
        pre101 = FOLD_ROOT / "101-release-checklist-generation.zip.pre-runtime-boundary-chain.bak"
        check("pre_088_backup_present", pre088.exists(), str(pre088))
        check("pre_101_backup_present", pre101.exists(), str(pre101))

        s061 = read_zip_text(z061, "repository-draft-generation/SKILL.md")
        o061 = read_zip_text(z061, "repository-draft-generation/references/repository-output-contract.yaml")
        c061 = read_zip_text(z061, "repository-draft-generation/references/repository-self-check.yaml")
        check("061_has_production_boundary_manifest", "production_boundary_manifest" in s061 and "R12_production_boundary_manifest" in s061)
        check("061_contract_has_boundary_manifest", "production_boundary_manifest" in o061 and "evidence_tier_required" in o061)
        check("061_self_check_rejects_missing_manifest", "R12_production_boundary_manifest" in c061)

        s066 = read_zip_text(z066, "sql-draft-generation/SKILL.md")
        o066 = read_zip_text(z066, "sql-draft-generation/references/output-template.md")
        c066 = read_zip_text(z066, "sql-draft-generation/references/sql-self-check.yaml")
        check("066_has_schema_runtime_manifest", "schema_runtime_boundary_manifest" in s066 and "R11_schema_runtime_boundary_manifest" in s066)
        check("066_template_has_schema_runtime_manifest", "schema_runtime_boundary_manifest" in o066)
        check("066_self_check_rejects_missing_schema_manifest", "R11_schema_runtime_boundary_manifest" in c066)

        s088 = read_zip_text(z088, "test-automation-orchestration/SKILL.md")
        t088 = read_zip_text(z088, "test-automation-orchestration/references/output-template.md")
        v088 = read_zip_text(z088, "test-automation-orchestration/scripts/validate_runtime_matrix.py")
        check("088_has_runtime_matrix_contract", "runtime_integration_evidence_matrix" in s088 and "R08_runtime_matrix_complete" in s088)
        check("088_template_has_runtime_matrix", "runtime_integration_evidence_matrix" in t088)
        check("088_validator_present", "validate_runtime_matrix.py" in "\n".join(zipfile.ZipFile(z088).namelist()) and "missing matrix rows" in v088)

        s101 = read_zip_text(z101, "release-checklist-generation/SKILL.md")
        t101 = read_zip_text(z101, "release-checklist-generation/references/output-template.md")
        r101 = read_zip_text(z101, "release-checklist-generation/references/readiness-inheritance.md")
        v101 = read_zip_text(z101, "release-checklist-generation/scripts/validate_artifact.py")
        check("101_consumes_runtime_rollup", "runtime_boundary_evidence_rollup" in s101 and "runtime_boundary_clearance" in s101)
        check("101_template_has_clearance", "runtime_boundary_clearance" in t101)
        check("101_readiness_blocks_uncleared_runtime", "Runtime boundary inheritance" in r101)
        check("101_validator_blocks_green_false_clearance", "RUNTIME-CLEARANCE" in v101)

        with tempfile.TemporaryDirectory(prefix="codex-runtime-chain-") as raw:
            tmp = Path(raw)
            post088 = extract_zip(z088, tmp / "post088")
            post101 = extract_zip(z101, tmp / "post101")
            pre088_root = extract_zip(pre088, tmp / "pre088") if pre088.exists() else None
            pre101_root = extract_zip(pre101, tmp / "pre101") if pre101.exists() else None

            check("ab_pre_088_lacks_matrix_validator", pre088_root is not None and not (pre088_root / "scripts" / "validate_runtime_matrix.py").exists())

            bad_missing = write_json(
                tmp / "088-bad-missing.json",
                {
                    "production_boundary_manifest": [{"boundary_id": "DB-001", "release_critical": True}],
                    "runtime_integration_evidence_matrix": [],
                },
            )
            bad_overclaim = write_json(
                tmp / "088-bad-overclaim.json",
                {
                    "production_boundary_manifest": [{"boundary_id": "DB-001", "release_critical": True}],
                    "runtime_integration_evidence_matrix": [
                        {
                            "boundary_id": "DB-001",
                            "evidence_tier": "self_contained_runtime",
                            "gate_effect": "block_release",
                            "gate_decision": "pass",
                        }
                    ],
                },
            )
            good088 = write_json(
                tmp / "088-good.json",
                {
                    "production_boundary_manifest": [{"boundary_id": "DB-001", "release_critical": True}],
                    "runtime_integration_evidence_matrix": [
                        {
                            "boundary_id": "DB-001",
                            "evidence_tier": "production_external_integration",
                            "gate_effect": "block_release",
                            "gate_decision": "pass",
                        }
                    ],
                },
            )
            v088_path = post088 / "scripts" / "validate_runtime_matrix.py"
            check("ab_post_088_missing_matrix_fails", run([sys.executable, str(v088_path), str(bad_missing)]).returncode != 0)
            check("ab_post_088_overclaim_fails", run([sys.executable, str(v088_path), str(bad_overclaim)]).returncode != 0)
            check("ab_post_088_good_passes", run([sys.executable, str(v088_path), str(good088)]).returncode == 0)
            check("088_post_self_test_passes", run([sys.executable, str(post088 / "scripts" / "test_skill.py")], post088).returncode == 0)

            bad101_text = """```yaml
metadata:
  readiness: green
  emit_event: {event_name: produced.release-prep.release_checklist.v2}
evidence_profile: {confirmed_evidence: []}
runtime_boundary_evidence_rollup:
  - boundary_id: DB-001
    gate_effect: block_release
    evidence_tier: self_contained_runtime
    gate_decision: conditional
runtime_boundary_clearance:
  - boundary_id: DB-001
    clearance_decision: conditional
self_check: {passed: true}
downstream_handoff: {}
adversarial_detection: none_detected
feedback_signal_candidates: []
confidence: high
```
"""
            good101_text = bad101_text.replace("readiness: green", "readiness: amber")
            bad101 = write_text(tmp / "101-bad.md", bad101_text)
            good101 = write_text(tmp / "101-good.md", good101_text)
            if pre101_root is not None:
                pre_bad = run([sys.executable, str(pre101_root / "scripts" / "validate_artifact.py"), str(bad101)])
                check("ab_pre_101_bad_sample_passes_old_validator", pre_bad.returncode == 0, pre_bad.stdout + pre_bad.stderr)
            post_bad = run([sys.executable, str(post101 / "scripts" / "validate_artifact.py"), str(bad101)])
            check("ab_post_101_bad_sample_fails", post_bad.returncode != 0, post_bad.stdout + post_bad.stderr)
            check("ab_post_101_bad_mentions_runtime", "RUNTIME-CLEARANCE" in (post_bad.stdout + post_bad.stderr))
            post_good = run([sys.executable, str(post101 / "scripts" / "validate_artifact.py"), str(good101)])
            check("ab_post_101_good_amber_passes", post_good.returncode == 0, post_good.stdout + post_good.stderr)

    except Exception as exc:  # pragma: no cover
        failed.append(f"exception:{exc}")

    status = "pass" if not failed else "fail"
    if args.summary_line:
        print(
            "CODEX-RUNTIME-BOUNDARY-CHAIN-FOLD "
            f"status={status} checks={len(checks)} library_zips={len(canonical_skill_zips())} "
            f"failed={'-' if not failed else '|'.join(failed)}"
        )
    else:
        print(f"status={status}")
        print(f"checks={len(checks)}")
        for item in failed:
            print(f"- {item}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
