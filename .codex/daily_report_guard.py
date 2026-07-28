#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guard daily Agent report style against drifting into delivery checklists."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
DAILY_DIR = ROOT / "日报"


@dataclass
class Check:
    name: str
    ok: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "ok": self.ok, "detail": self.detail}


def as_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def daily_path(day: str) -> Path:
    return DAILY_DIR / f"CD1-{day}-日报-Agent板块.md"


def heading_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.startswith("#")]


def bullet_density(text: str) -> tuple[int, int, float]:
    lines = [line for line in text.splitlines() if line.strip()]
    bullets = [line for line in lines if re.match(r"\s*[-*]\s+", line)]
    density = len(bullets) / max(1, len(lines))
    return len(bullets), len(lines), density


def check_report(path: Path) -> dict[str, Any]:
    checks: list[Check] = [Check("file-exists", path.is_file(), as_posix(path))]
    if not path.exists():
        return {"status": "fail", "path": as_posix(path), "checks": [item.to_dict() for item in checks]}

    text = path.read_text(encoding="utf-8")
    headings = heading_lines(text)
    bullets, nonempty_lines, density = bullet_density(text)

    required_exact = [
        "# CD1 日报 Agent 板块",
        "## 今日主线",
        "## 明日候选",
    ]
    for token in required_exact:
        checks.append(Check(f"heading-token:{token}", token in text, token))

    ordered_markers = [
        "## 今日主线",
        "## 一 ",
        "## 二 ",
        "## 三 ",
        "## 明日候选",
    ]
    positions = [text.find(marker) for marker in ordered_markers]
    checks.append(
        Check(
            "old-daily-heading-order",
            all(pos >= 0 for pos in positions) and positions == sorted(positions),
            " | ".join(f"{marker}:{pos}" for marker, pos in zip(ordered_markers, positions)),
        )
    )
    checks.append(Check("narrative-length", len(text) >= 3000, f"{len(text)} chars; min=3000"))
    checks.append(Check("not-checklist-dominant", density <= 0.18, f"bullets={bullets}, lines={nonempty_lines}, density={density:.2f}"))
    checks.append(Check("archive-pointer", "归档指针" in text, "归档指针"))
    checks.append(Check("mainline-and-status", "今日主线" in text and "纪律与状态" in text, "今日主线 + 纪律与状态"))
    checks.append(Check("no-marketing-summary", "完成项" not in headings and "验证" not in headings, "avoid delivery-summary section names as top-level style"))
    if "2026-07-27" in path.name:
        day_scope_tokens = ["B-design", "D-code", "TEST", "REL", "OPS", "DOC", "CMP", "PLAT", "BAR-EVAL", ".codex"]
        present = [token for token in day_scope_tokens if token in text]
        checks.append(Check("day-scope-not-latest-session-only", len(present) >= 8, ",".join(present)))
        full_chain_tokens = [
            "PARSE",
            "B-design",
            "C-task",
            "D-code",
            "TEST",
            "REL",
            "OPS",
            "DOC",
            "CMP",
            "PLAT",
            "INTEG",
            "FIND4",
            "BAR-EVAL",
        ]
        first_slice = text[:1600]
        full_chain_present = [token for token in full_chain_tokens if token in first_slice]
        checks.append(
            Check(
                "a3-full-chain-first",
                "## 一 A3 全链路 shakedown 的内容主线" in text and len(full_chain_present) == len(full_chain_tokens),
                ",".join(full_chain_present),
            )
        )
        checks.append(
            Check(
                "findings-after-full-chain",
                "这是跑完整链路后的发现，不是今天主线本身" in text,
                "graph/tree findings must be framed as an output of full-chain shakedown",
            )
        )
        content_signal_tokens = [
            "not_globally_generated_gte_team",
            "NO_GO",
            "tree_path",
            "J1",
            "HC",
            "source+target",
            "PRE<POST",
            "157",
        ]
        content_present = [token for token in content_signal_tokens if token in text]
        checks.append(Check("content-first-signals", len(content_present) >= 6, ",".join(content_present)))
        checks.append(Check("not-tail-only-heading", "A3 后续阶段正式收官" not in text, "forbid latest-session heading as day scope"))
        project_path_hits = len(re.findall(r"D:/projects/skills-pilot", text))
        checks.append(Check("not-artifact-path-index", project_path_hits <= 4, f"D:/projects/skills-pilot hits={project_path_hits}"))
        forbidden_artifact_dump_phrases = ["产物目录是", "分别落在", "产物落在", "分数卡是"]
        found_phrases = [phrase for phrase in forbidden_artifact_dump_phrases if phrase in text]
        checks.append(Check("no-artifact-dump-phrasing", not found_phrases, ",".join(found_phrases) or "-"))

    ok = all(item.ok for item in checks)
    return {
        "status": "pass" if ok else "fail",
        "path": as_posix(path),
        "headings": headings,
        "checks": [item.to_dict() for item in checks],
    }


def summary(result: dict[str, Any]) -> str:
    checks = result["checks"]
    passed = sum(1 for item in checks if item["ok"])
    failed = ",".join(item["name"] for item in checks if not item["ok"]) or "-"
    return f"CODEX-DAILY-REPORT-GUARD status={result['status']} checks={passed}/{len(checks)} failed={failed} path={result['path']}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--summary-line", action="store_true")
    args = parser.parse_args()

    result = check_report(daily_path(args.date))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.summary_line:
        print(summary(result))
    else:
        print(summary(result))
        for check in result["checks"]:
            print(f"{'OK' if check['ok'] else 'FAIL'} {check['name']}: {check['detail']}")
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
