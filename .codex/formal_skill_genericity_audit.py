#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parents[1]
EXPECTED_LIBRARY_ZIPS = 157
TEXT_EXTENSIONS = {".md", ".yaml", ".yml", ".py", ".json", ".txt", ".csv"}


@dataclass(frozen=True)
class PatternRule:
    name: str
    pattern: re.Pattern[str]


BANNED_FORMAL_TOKENS = [
    PatternRule("oa1-oa2-label", re.compile(r"\bOA[12]\b")),
    PatternRule("hub-oa-reference", re.compile(r"\bhub-oa\b", re.IGNORECASE)),
    PatternRule("b2-approval-module-label", re.compile(r"\bB2-approval\b", re.IGNORECASE)),
    PatternRule("z1-risk-module-label", re.compile(r"\bZ1[-_ ](?:risk|风控)\b", re.IGNORECASE)),
    PatternRule("watchdog-project-label", re.compile(r"\bwatchdog\b", re.IGNORECASE)),
    PatternRule("wflow-product-label", re.compile(r"\bwflow\b", re.IGNORECASE)),
    PatternRule("ticket-mapper-example", re.compile(r"\bticket_mapper\b", re.IGNORECASE)),
    PatternRule("local-oa2-boundary", re.compile(r"\bLOCAL-OA2\b", re.IGNORECASE)),
    PatternRule("real-tg-evidence-mode", re.compile(r"\breal_tg\b", re.IGNORECASE)),
    PatternRule("real-kms-evidence-mode", re.compile(r"\breal_kms\b", re.IGNORECASE)),
    PatternRule("real-alertcenter-evidence-mode", re.compile(r"\breal_alertcenter\b", re.IGNORECASE)),
    PatternRule(
        "tg-boundary-or-evidence-type",
        re.compile(r"\b(?:boundary_type|evidence_mode|evidence_modes|enum)\b.*\btg\b", re.IGNORECASE),
    ),
    PatternRule("alertcenter-boundary-type", re.compile(r"\balertcenter\b", re.IGNORECASE)),
]


def canonical_skill_zips() -> list[Path]:
    return [p for p in REPO.rglob("*.zip") if any(part == "完稿" for part in p.parts)]


def find_one(zip_name: str) -> Path:
    matches = [p for p in canonical_skill_zips() if p.name == zip_name]
    if len(matches) != 1:
        raise AssertionError(f"expected exactly one formal {zip_name}, found {len(matches)}")
    return matches[0]


def iter_zip_text(zip_path: Path):
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.namelist():
            if member.endswith("/"):
                continue
            if Path(member).suffix.lower() not in TEXT_EXTENSIONS:
                continue
            try:
                yield member, zf.read(member).decode("utf-8")
            except UnicodeDecodeError:
                continue


def zip_text(zip_name: str, member_suffix: str) -> str:
    zip_path = find_one(zip_name)
    for member, text in iter_zip_text(zip_path):
        if member.endswith(member_suffix):
            return text
    raise AssertionError(f"{zip_name} missing member ending {member_suffix}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()

    failures: list[str] = []
    checks: list[str] = []

    zips = canonical_skill_zips()
    checks.append("library_zip_count_157")
    if len(zips) != EXPECTED_LIBRARY_ZIPS:
        failures.append(f"library_zip_count expected={EXPECTED_LIBRARY_ZIPS} actual={len(zips)}")

    banned_hits: list[str] = []
    for zip_path in zips:
        for member, text in iter_zip_text(zip_path):
            for line_no, line in enumerate(text.splitlines(), 1):
                for rule in BANNED_FORMAL_TOKENS:
                    if rule.pattern.search(line):
                        banned_hits.append(
                            f"{zip_path.name}::{member}:{line_no}:{rule.name}:{line.strip()[:160]}"
                        )
    checks.append("no_project_specific_tokens_in_formal_zips")
    if banned_hits:
        failures.extend(banned_hits)

    required_replacements = {
        "060-service-draft-generation.zip": {
            "service-draft-generation/SKILL.md": ["workflow-engine callback", "key-management"],
            "service-draft-generation/references/service-algorithms.yaml": ["external workflow-engine/webhook callback"],
            "service-draft-generation/references/service-self-check.yaml": ["key-management infrastructure"],
        },
        "088-test-automation-orchestration.zip": {
            "test-automation-orchestration/references/output-template.md": ["production_surface: primary_repository"],
            "test-automation-orchestration/references/v2-output-contract.md": [
                "notification_gateway",
                "key_management",
                "alerting_platform",
            ],
        },
        "093-quality-gate-check.zip": {
            "quality-gate-check/references/output-template.md": [
                "real_notification_gateway",
                "real_key_management",
                "real_alerting_platform",
            ],
            "quality-gate-check/references/validation-rules.md": [
                "notification/key-management/alerting/scheduler/external-system"
            ],
            "quality-gate-check/scripts/test_skill.py": ['"boundary_id": "LOCAL-RUNTIME"'],
            "quality-gate-check/scripts/validate_n260_output.py": [
                '"real_notification_gateway"',
                '"real_key_management"',
                '"real_alerting_platform"',
            ],
        },
    }
    for zip_name, members in required_replacements.items():
        for member, tokens in members.items():
            text = zip_text(zip_name, member)
            for token in tokens:
                check_name = f"{zip_name}:{member}:{token}"
                checks.append(check_name)
                if token not in text:
                    failures.append(f"missing_required_generic_token {check_name}")

    status = "pass" if not failures else "fail"
    if args.summary_line:
        failed = "-" if not failures else ";".join(failures[:5])
        print(
            "CODEX-FORMAL-SKILL-GENERICITY "
            f"status={status} checks={len(checks)} library_zips={len(zips)} failed={failed}"
        )
    else:
        print(f"status={status}")
        print(f"checks={len(checks)}")
        print(f"library_zips={len(zips)}")
        if failures:
            print("failures:")
            for failure in failures:
                print(f"- {failure}")
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
