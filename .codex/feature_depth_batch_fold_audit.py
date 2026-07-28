#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parents[1]
FOLD_ROOT = Path(
    "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/"
    "b2-z1-standalone-production-code/FOLD-FEATURE-DEPTH-BATCH"
)
EXPECTED_LIBRARY_ZIPS = 157


def canonical_skill_zips() -> list[Path]:
    return [p for p in REPO.rglob("*.zip") if any(part == "完稿" for part in p.parts)]


def find_one(zip_name: str) -> Path:
    matches = [p for p in canonical_skill_zips() if p.name == zip_name]
    if len(matches) != 1:
        raise AssertionError(f"expected exactly one formal {zip_name}, found {len(matches)}")
    return matches[0]


def read_zip_text(zip_path: Path, member: str) -> str:
    with zipfile.ZipFile(zip_path) as zf:
        return zf.read(member).decode("utf-8")


def has_member(zip_path: Path, member: str) -> bool:
    with zipfile.ZipFile(zip_path) as zf:
        return member in zf.namelist()


def extract_zip(zip_path: Path, dest: Path) -> Path:
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)
    roots = [p for p in dest.iterdir() if p.is_dir()]
    if len(roots) != 1:
        raise AssertionError(f"expected one root in {zip_path}, got {roots}")
    return roots[0]


def run_validator(validator: Path, doc: dict[str, Any]) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
        json.dump(doc, fh)
        path = Path(fh.name)
    try:
        return subprocess.run([sys.executable, str(validator), str(path)], capture_output=True, text=True, encoding="utf-8")
    finally:
        try:
            path.unlink()
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()

    checks: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, ok, detail))

    zips = canonical_skill_zips()
    check("library_zip_count_157", len(zips) == EXPECTED_LIBRARY_ZIPS, str(len(zips)))

    zip060 = find_one("060-service-draft-generation.zip")
    zip061 = find_one("061-repository-draft-generation.zip")
    zip088 = find_one("088-test-automation-orchestration.zip")
    pre060 = FOLD_ROOT / "060-service-draft-generation.zip.pre-feature-depth-batch.bak"
    pre061 = FOLD_ROOT / "061-repository-draft-generation.zip.pre-feature-depth-batch.bak"
    pre088 = FOLD_ROOT / "088-test-automation-orchestration.zip.pre-feature-depth-batch.bak"
    for path in (pre060, pre061, pre088):
        check(f"pre_backup_exists:{path.name}", path.exists(), str(path))

    current060_skill = read_zip_text(zip060, "service-draft-generation/SKILL.md")
    current060_alg = read_zip_text(zip060, "service-draft-generation/references/service-algorithms.yaml")
    current060_contract = read_zip_text(zip060, "service-draft-generation/references/service-output-contract.yaml")
    current060_check = read_zip_text(zip060, "service-draft-generation/references/service-self-check.yaml")
    pre060_skill = read_zip_text(pre060, "service-draft-generation/SKILL.md")
    pre060_alg = read_zip_text(pre060, "service-draft-generation/references/service-algorithms.yaml")
    check("pre060_lacked_feature_depth_gate", "R_IMPL_FEATURE_DEPTH_OBLIGATIONS" not in pre060_skill + pre060_alg)
    for token in (
        "feature_depth_obligations",
        "feature_depth_obligation_inference",
        "FD-001",
        "FD-002",
        "FD-003",
        "FD-004",
        "R_IMPL_FEATURE_DEPTH_OBLIGATIONS",
    ):
        check(f"post060_contains:{token}", token in current060_skill + current060_alg + current060_contract + current060_check)

    current061_skill = read_zip_text(zip061, "repository-draft-generation/SKILL.md")
    current061_alg = read_zip_text(zip061, "repository-draft-generation/references/repository-algorithms.yaml")
    current061_contract = read_zip_text(zip061, "repository-draft-generation/references/repository-output-contract.yaml")
    current061_check = read_zip_text(zip061, "repository-draft-generation/references/repository-self-check.yaml")
    pre061_text = read_zip_text(pre061, "repository-draft-generation/SKILL.md") + read_zip_text(
        pre061, "repository-draft-generation/references/repository-output-contract.yaml"
    )
    check("pre061_lacked_read_side_security_filters", "read_side_security_filters" not in pre061_text)
    for token in ("read_side_security_filters", "R13_read_side_security_filters", "RSF-001", "mirror_read_side_filter"):
        check(f"post061_contains:{token}", token in current061_skill + current061_alg + current061_contract + current061_check)

    current088_skill = read_zip_text(zip088, "test-automation-orchestration/SKILL.md")
    current088_contract = read_zip_text(zip088, "test-automation-orchestration/references/v2-output-contract.md")
    current088_rules = read_zip_text(zip088, "test-automation-orchestration/references/v2-rules.md")
    pre088_text = read_zip_text(pre088, "test-automation-orchestration/SKILL.md") + read_zip_text(
        pre088, "test-automation-orchestration/references/v2-output-contract.md"
    )
    check("pre088_lacked_feature_depth_matrix", "feature_depth_test_matrix" not in pre088_text)
    check(
        "post088_has_feature_depth_validator",
        has_member(zip088, "test-automation-orchestration/scripts/validate_feature_depth_matrix.py"),
    )
    for token in ("feature_depth_test_matrix", "R09_feature_depth_matrix_complete", "R11_feature_depth_matrix_complete"):
        check(f"post088_contains:{token}", token in current088_skill + current088_contract + current088_rules)

    with tempfile.TemporaryDirectory() as tmp:
        root = extract_zip(zip088, Path(tmp) / "088")
        test_skill = root / "scripts" / "test_skill.py"
        result = subprocess.run([sys.executable, str(test_skill)], capture_output=True, text=True, encoding="utf-8")
        check("post088_self_test_pass", result.returncode == 0, result.stdout[-200:])
        validator = root / "scripts" / "validate_feature_depth_matrix.py"
        bad_missing = {
            "feature_depth_obligations": [{"obligation_id": "FD-001", "obligation_type": "source_backed_eligibility"}],
            "feature_depth_test_matrix": [],
        }
        bad_happy_only = {
            "feature_depth_obligations": [{"obligation_id": "FD-002", "obligation_type": "business_calendar_temporal_policy"}],
            "feature_depth_test_matrix": [{
                "obligation_id": "FD-002",
                "obligation_type": "business_calendar_temporal_policy",
                "positive_case_refs": ["TC-positive"],
                "negative_case_refs": [],
                "executed_evidence_ref": "junit://TC-positive",
                "status": "pass",
                "gate_decision": "pass",
            }],
        }
        good_depth = {
            "feature_depth_obligations": [{"obligation_id": "FD-003", "obligation_type": "enumerated_detector_breadth"}],
            "read_side_security_filters": [{"filter_id": "RSF-001", "query_ref": "query.list"}],
            "feature_depth_test_matrix": [
                {
                    "obligation_id": "FD-003",
                    "obligation_type": "enumerated_detector_breadth",
                    "positive_case_refs": ["TC-positive"],
                    "negative_case_refs": ["TC-negative"],
                    "executed_evidence_ref": "junit://TC-enum",
                    "status": "pass",
                    "gate_decision": "pass",
                },
                {
                    "obligation_id": "RSF-001",
                    "obligation_type": "read_side_security_filter",
                    "positive_case_refs": ["TC-allowed"],
                    "negative_case_refs": ["TC-denied"],
                    "executed_evidence_ref": "junit://TC-read-filter",
                    "status": "pass",
                    "gate_decision": "pass",
                },
            ],
        }
        check("feature_depth_bad_missing_fails", run_validator(validator, bad_missing).returncode != 0)
        check("feature_depth_happy_only_fails", run_validator(validator, bad_happy_only).returncode != 0)
        check("feature_depth_good_passes", run_validator(validator, good_depth).returncode == 0)

    failures = [c for c in checks if not c[1]]
    status = "pass" if not failures else "fail"
    if args.summary_line:
        failed = "-" if not failures else ";".join(f"{name}:{detail}" for name, _, detail in failures[:5])
        print(f"CODEX-FEATURE-DEPTH-BATCH-FOLD status={status} checks={len(checks)} library_zips={len(zips)} failed={failed}")
    else:
        print(f"status={status}")
        for name, ok, detail in checks:
            mark = "PASS" if ok else "FAIL"
            print(f"{mark} {name} {detail}")
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
