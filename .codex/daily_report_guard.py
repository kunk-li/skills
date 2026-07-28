#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guard daily Agent report style against drifting into vague narrative."""

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


def is_fact_report_day(day: str) -> bool:
    return day >= "2026-07-28"


def long_paragraph_count(text: str) -> int:
    count = 0
    for block in text.split("\n\n"):
        stripped = block.lstrip()
        if stripped.startswith(("-", "#")):
            continue
        if len(" ".join(block.split())) >= 220:
            count += 1
    return count


def check_fact_report(text: str, headings: list[str], checks: list[Check]) -> None:
    bullets, nonempty_lines, density = bullet_density(text)
    checks.append(Check("fact-content-bullet-density", density >= 0.18, f"bullets={bullets}, lines={nonempty_lines}, density={density:.2f}"))
    checks.append(Check("few-long-paragraphs", long_paragraph_count(text) <= 2, f"long_paragraphs={long_paragraph_count(text)}"))
    checks.append(Check("fact-length-band", 2200 <= len(text) <= 8000, f"{len(text)} chars; expected 2200..8000"))

    required_fact_tokens = [
        "Z1",
        "B2",
        "OA2",
        "原型",
        "060",
        "093",
        "061",
        "066",
        "088",
        "101",
        "NO_GO",
        "2/11",
        "commit",
        "push",
    ]
    present = [token for token in required_fact_tokens if token in text]
    checks.append(Check("factual-content-tokens", len(present) >= 12, ",".join(present)))
    required_fact_phrases = ["跑了", "修了", "优化", "验证", "commit", "push"]
    present_phrases = [phrase for phrase in required_fact_phrases if phrase in text]
    checks.append(Check("daily-fact-verbs", len(present_phrases) == len(required_fact_phrases), ",".join(present_phrases)))

    forbidden_report_phrases = [
        "今天真正完成的是",
        "今天的价值",
        "最重要",
        "最有价值",
        "结论很硬",
        "显微镜",
        "一句话",
        "不是单纯",
        "不是终点",
    ]
    found = [phrase for phrase in forbidden_report_phrases if phrase in text]
    checks.append(Check("no-vague-report-phrasing", not found, ",".join(found) or "-"))
    checks.append(Check("no-marketing-summary", "完成项" not in headings, "avoid delivery-summary section names as top-level style"))


def check_legacy_report(text: str, headings: list[str], checks: list[Check], path: Path) -> None:
    day_match = re.search(r"CD1-(\d{4}-\d{2}-\d{2})-", path.name)
    fact_day = bool(day_match and is_fact_report_day(day_match.group(1)))
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
    bullets, nonempty_lines, density = bullet_density(text)
    if not fact_day:
        checks.append(Check("not-checklist-dominant", density <= 0.18, f"bullets={bullets}, lines={nonempty_lines}, density={density:.2f}"))
    checks.append(Check("archive-pointer", "归档指针" in text, "归档指针"))
    checks.append(Check("mainline-and-status", "今日主线" in text and "纪律与状态" in text, "今日主线 + 纪律与状态"))
    checks.append(Check("no-marketing-summary", "完成项" not in headings and "验证" not in headings, "avoid delivery-summary section names as top-level style"))
    if fact_day:
        check_fact_report(text, headings, checks)

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


def check_report(path: Path, day: str) -> dict[str, Any]:
    checks: list[Check] = [Check("file-exists", path.is_file(), as_posix(path))]
    if not path.exists():
        return {"status": "fail", "path": as_posix(path), "checks": [item.to_dict() for item in checks]}

    text = path.read_text(encoding="utf-8")
    headings = heading_lines(text)
    check_legacy_report(text, headings, checks, path)

    ok = all(item.ok for item in checks)
    return {
        "status": "pass" if ok else "fail",
        "path": as_posix(path),
        "headings": headings,
        "checks": [item.to_dict() for item in checks],
    }


def check_text_report(text: str, path_name: str) -> dict[str, Any]:
    checks = [Check("file-exists", True, path_name)]
    headings = heading_lines(text)
    check_legacy_report(text, headings, checks, Path(path_name))
    ok = all(item.ok for item in checks)
    return {
        "status": "pass" if ok else "fail",
        "path": path_name,
        "headings": headings,
        "checks": [item.to_dict() for item in checks],
    }


def fact_style_fixture() -> str:
    facts = "\n".join(
        [
            "- 跑了 Z1 风控模块，CMP 从 10/19 修到 18/19，仍保留生产集成缺口。",
            "- 跑了 B2 审批模块，当前 NO_GO，bar 为 2/11。",
            "- 跑了 OA2 独立代码包，验证 `OA2_SELF_CONTAINED_SMOKE passed=16`。",
            "- 跑了原型分析，使用 019、020、021、025、029、051、052。",
            "- 修了 D-code 绕过 060 implement 的问题。",
            "- 修了 OA1/OA2 绑定口径错误。",
            "- 优化 043、044、093 三个硬折。",
            "- 优化 061、066、088、101 runtime boundary chain。",
            "- 优化 060、061、088 feature-depth batch。",
            "- 验证 daily report guard、UTF-8 guard、project guard。",
            "- commit `abc1234`，push `origin/main`。",
        ]
        * 3
    )
    return f"""# CD1 日报 Agent 板块 2026-07-28

## 今日主线

今天按旧日报样式陈述事实。

## 一 跑了哪些模块

{facts}

## 二 修了哪些问题

{facts}

## 三 做了哪些优化

{facts}

## 纪律与状态

{facts}

## 明日候选

继续内部自动队列，不是用户待办。

归档指针：`D:/work/资料/skills/STATUS.md`。
"""


def new_heading_fixture() -> str:
    return fact_style_fixture().replace("## 今日主线", "## 今日事实").replace("## 一 跑了哪些模块", "## 跑了哪些模块")


def vague_report_fixture() -> str:
    return fact_style_fixture().replace("今天按旧日报样式陈述事实。", "今天真正完成的是一次最重要的价值复盘。")


def self_test_payload() -> dict[str, Any]:
    cases = [
        ("old_style_fact_passes", fact_style_fixture(), "pass"),
        ("new_heading_structure_fails", new_heading_fixture(), "fail"),
        ("vague_report_prose_fails", vague_report_fixture(), "fail"),
    ]
    checks = []
    for name, text, expected in cases:
        result = check_text_report(text, "CD1-2026-07-28-日报-Agent板块.md")
        checks.append({"name": name, "ok": result["status"] == expected, "detail": result["status"]})
    failed = [item["name"] for item in checks if not item["ok"]]
    return {"status": "pass" if not failed else "fail", "checks": checks, "failed": failed}


def self_test_summary(payload: dict[str, Any]) -> str:
    checks = payload["checks"]
    passed = sum(1 for item in checks if item["ok"])
    failed = ",".join(payload["failed"]) or "-"
    return f"CODEX-DAILY-REPORT-GUARD-SELFTEST status={payload['status']} checks={passed}/{len(checks)} failed={failed}"


def summary(result: dict[str, Any]) -> str:
    checks = result["checks"]
    passed = sum(1 for item in checks if item["ok"])
    failed = ",".join(item["name"] for item in checks if not item["ok"]) or "-"
    return f"CODEX-DAILY-REPORT-GUARD status={result['status']} checks={passed}/{len(checks)} failed={failed} path={result['path']}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="YYYY-MM-DD")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--summary-line", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        payload = self_test_payload()
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(self_test_summary(payload))
        return 0 if payload["status"] == "pass" else 2

    if not args.date:
        parser.error("--date is required unless --self-test is used")

    result = check_report(daily_path(args.date), args.date)
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
