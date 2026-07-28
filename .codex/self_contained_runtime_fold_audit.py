#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
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
    "b2-z1-standalone-production-code/FOLD-060-093-SELF-CONTAINED-RUNTIME"
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
    names = [p for p in dest.iterdir() if p.is_dir()]
    if len(names) != 1:
        raise AssertionError(f"expected one extracted root in {dest}, found {len(names)}")
    return names[0]


def base_quality_doc(readiness: str = "pass") -> dict:
    return {
        "metadata": {
            "schema_version": "2.1",
            "governance_revision": "3.1.3",
            "skill_id": "quality-gate-check",
            "workflow_node": "N260",
            "selected_mode": "full_gate",
            "readiness": readiness,
            "evidence_profile": "direct_contract",
            "routing": {},
            "event_contract": {"produces_event": "produced.n260.quality_gate_check"},
            "signal_emission": {"to_n005": False},
            "human_review": {},
            "schema_evolution": {},
        },
        "gate_summary": {},
        "final_verdict": "pass",
        "release_gate": "pass",
    }


def write_json(path: Path, doc: dict) -> Path:
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def run_validator(skill_root: Path, artifact: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(skill_root / "scripts" / "validate_n260_output.py"),
            "--skill",
            "quality-gate-check",
            "--domain-mode",
            "complete",
            str(artifact),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


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
        zips = canonical_skill_zips()
        check("library_zip_count_157", len(zips) == EXPECTED_LIBRARY_ZIPS, str(len(zips)))

        z060 = find_one("060-service-draft-generation.zip")
        z093 = find_one("093-quality-gate-check.zip")

        s060 = read_zip_text(z060, "service-draft-generation/SKILL.md")
        c060 = read_zip_text(z060, "service-draft-generation/references/service-self-check.yaml")
        a060 = read_zip_text(z060, "service-draft-generation/references/service-algorithms.yaml")
        check("060_skill_has_self_contained_gate", "R_IMPL_SELF_CONTAINED_RUNTIME" in s060)
        check("060_contract_has_runtime_package", "self_contained_runtime_package" in s060 and "delivery_scope" in s060)
        check("060_self_check_has_runtime_gate", "R_IMPL_SELF_CONTAINED_RUNTIME" in c060)
        check("060_algorithms_require_runtime_package", "self_contained_runtime_package" in a060 and "self_contained_runtime_required_when" in a060)

        s093 = read_zip_text(z093, "quality-gate-check/SKILL.md")
        o093 = read_zip_text(z093, "quality-gate-check/references/output-template.md")
        r093 = read_zip_text(z093, "quality-gate-check/references/validation-rules.md")
        v093 = read_zip_text(z093, "quality-gate-check/scripts/validate_n260_output.py")
        t093 = read_zip_text(z093, "quality-gate-check/scripts/test_skill.py")
        check("093_skill_has_three_tiers", all(token in s093 for token in ["reference_only", "self_contained_runtime", "production_external_integration"]))
        check("093_template_has_evidence_tier", "evidence_tier" in o093 and "self_contained_runtime_status" in o093)
        check("093_rules_define_self_contained_boundary", "Self-contained runtime evidence is its own tier" in r093)
        check("093_validator_has_tier_sets", all(token in v093 for token in ["SELF_CONTAINED_RUNTIME_EVIDENCE_MODES", "PRODUCTION_EXTERNAL_INTEGRATION_EVIDENCE_MODES", "classify_runtime_evidence_tier"]))
        check("093_test_has_prevent_overclaim_case", "release-blocking self-contained runtime overclaim" in t093)

        pre093 = FOLD_ROOT / "093-quality-gate-check.zip.pre-self-contained-runtime.bak"
        check("pre_093_backup_present", pre093.exists(), str(pre093))

        with tempfile.TemporaryDirectory(prefix="codex-093-fold-") as raw_tmp:
            tmp = Path(raw_tmp)
            post_root = extract_zip(z093, tmp / "post")
            pre_root = extract_zip(pre093, tmp / "pre") if pre093.exists() else None

            bad = base_quality_doc("pass")
            bad["runtime_integration_status"] = "runtime_integration_pass"
            bad["runtime_boundary_evidence_rollup"] = [
                {
                    "boundary_id": "B-DB",
                    "boundary_type": "db",
                    "evidence_mode": "standalone_smoke",
                    "gate_effect": "block_release",
                    "gate_decision": "pass",
                }
            ]
            bad_path = write_json(tmp / "bad-overclaim.json", bad)

            good = base_quality_doc("pass")
            good["self_contained_runtime_status"] = "pass"
            good["runtime_integration_status"] = "not_applicable"
            good["runtime_boundary_evidence_rollup"] = [
                {
                    "boundary_id": "LOCAL-OA2",
                    "boundary_type": "local_runtime",
                    "evidence_tier": "self_contained_runtime",
                    "evidence_mode": "standalone_smoke",
                    "gate_effect": "local_runtime_only",
                    "gate_decision": "pass",
                }
            ]
            good_path = write_json(tmp / "good-local-runtime.json", good)

            if pre_root is not None:
                pre_bad = run_validator(pre_root, bad_path)
                check("ab_pre_bad_sample_passes_old_validator", pre_bad.returncode == 0, pre_bad.stdout + pre_bad.stderr)
            post_bad = run_validator(post_root, bad_path)
            check("ab_post_bad_sample_fails_new_validator", post_bad.returncode != 0, post_bad.stdout + post_bad.stderr)
            check("ab_post_bad_mentions_self_contained", "self_contained" in (post_bad.stdout + post_bad.stderr).lower())

            post_good = run_validator(post_root, good_path)
            check("ab_post_good_local_runtime_passes", post_good.returncode == 0, post_good.stdout + post_good.stderr)

            test_result = subprocess.run(
                [sys.executable, str(post_root / "scripts" / "test_skill.py")],
                cwd=str(post_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            check("093_post_self_test_passes", test_result.returncode == 0, test_result.stdout + test_result.stderr)

    except Exception as exc:  # pragma: no cover
        failed.append(f"exception: {exc}")

    status = "pass" if not failed else "fail"
    if args.summary_line:
        print(
            "CODEX-SELF-CONTAINED-RUNTIME-FOLD "
            f"status={status} checks={len(checks)} "
            f"library_zips={len(canonical_skill_zips())} "
            f"failed={'-' if not failed else '|'.join(failed)}"
        )
        return 0 if not failed else 1

    print(f"status={status}")
    print(f"checks={len(checks)}")
    if failed:
        print("failed:")
        for item in failed:
            print(f"- {item}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
