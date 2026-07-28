#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DOC = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/b2-z1-standalone-production-code/OA2-OA1-GAP-ATTRIBUTION.md")

REQUIRED_TOKENS = [
    "OA1_REFERENCE_ONLY",
    "OA2_SELF_CONTAINED_CLOSED",
    "STILL_OPEN_PRODUCTION_EQUIVALENCE",
    "SKILL_FOLD_CANDIDATE",
    "reference_only",
    "self_contained_runtime",
    "production_external_integration",
    "060 gap confirmed",
    "093 gap confirmed",
    "closed_by_OA2_self_contained",
    "partial_after_OA2",
]

FORBIDDEN = [
    "OA1 is target",
    "bind OA2 to OA1",
    "OA2 target path",
    "hub-oa target path",
    "编入 hub-oa",
    "接真实 hub-oa",
    "逐文件映射",
    "patch/diff",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-line", action="store_true")
    parser.parse_args()

    checks = 0
    failures: list[str] = []

    checks += 1
    if not DOC.exists():
        failures.append("missing-doc")
        text = ""
    else:
        text = DOC.read_text(encoding="utf-8", errors="replace")

    for token in REQUIRED_TOKENS:
        checks += 1
        if token not in text:
            failures.append(f"missing-token:{token}")

    for token in FORBIDDEN:
        checks += 1
        if token.lower() in text.lower():
            failures.append(f"forbidden-token:{token}")

    for prefix, expected in [("B2-", 12), ("Z1-", 15)]:
        found = len(set(re.findall(rf"\|\s*({prefix}\d+)\s*\|", text)))
        checks += 1
        if found != expected:
            failures.append(f"{prefix}row-count:{found}!={expected}")

    checks += 1
    if "closed_by_OA2_self_contained | 12" not in text:
        failures.append("bad-closed-count")
    checks += 1
    if "partial_after_OA2 | 10" not in text:
        failures.append("bad-partial-count")
    checks += 1
    if "still_open_production_equivalence | 5" not in text:
        failures.append("bad-open-count")

    line_refs = re.findall(r"[A-Za-z0-9_./:\\-]+(?:\.java|\.xml|\.properties|pom\.xml):\d+", text)
    checks += 1
    if len(line_refs) < 30:
        failures.append(f"too-few-line-refs:{len(line_refs)}")

    status = "pass" if not failures else "fail"
    print(f"CODEX-OA2-OA1-GAP-ATTRIBUTION status={status} checks={checks} failed={','.join(failures) if failures else '-'}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
