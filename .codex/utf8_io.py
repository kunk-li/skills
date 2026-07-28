#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]

TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}
EXCLUDED_PARTS = {"__pycache__", "baselines", "node_modules", "reports", "tmp"}

MOJIBAKE_PATTERNS = [
    "\ufffd",
    "\u74a7\u52ec\u67a1",  # common mojibake for the workspace Chinese folder name
    "\u93c3\u30e6\u59e4",  # common mojibake for daily-report text
    "\u6d93\u837b\u568e",  # common mojibake for mainline text
    "\u6402",              # mojibake often seen instead of section sign
    "\u9225",
    "\u4e63",
    "\u701a\u5c6e\u5e4a",
]


@dataclass
class Finding:
    path: Path
    pattern: str
    count: int


def as_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def rel(path: Path) -> str:
    try:
        return as_posix(path.relative_to(ROOT))
    except ValueError:
        return as_posix(path)


def candidate_text_files() -> list[Path]:
    paths: list[Path] = []
    for root in [ROOT / ".codex"]:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            if any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts):
                continue
            paths.append(path)
    for name in [
        "AGENTS.md",
        "STATUS.md",
        "DECISIONS.md",
        "TOOL-HARDENING-PLAN.md",
        "CODEX-CODE-TIPS.md",
        "CLAUDE-CODE-TIPS.md",
    ]:
        path = ROOT / name
        if path.exists():
            paths.append(path)
    paths.extend(ROOT.glob("*/CD1-2026-07-27-*-Agent*.md"))
    return sorted(set(paths))


def resolve_patterns(patterns: list[str]) -> list[Path]:
    matches: list[Path] = []
    for item in patterns:
        raw = Path(item)
        if raw.is_absolute() and raw.exists():
            matches.append(raw)
            continue
        rooted = ROOT / item
        if rooted.exists():
            matches.append(rooted)
            continue
        matches.extend(ROOT.glob(item))
    return sorted({path.resolve() for path in matches if path.is_file()})


def read_file(path: Path, first: int | None, last: int | None) -> str:
    text = path.read_text(encoding="utf-8")
    if first is not None or last is not None:
        lines = text.splitlines()
        if first is not None:
            lines = lines[:first]
        if last is not None:
            lines = lines[-last:]
        text = "\n".join(lines)
        if text:
            text += "\n"
    return text


def scan_controlled_files() -> list[Finding]:
    findings: list[Finding] = []
    for path in candidate_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(Finding(path, "UTF-8 decode error", 1))
            continue
        for pattern in MOJIBAKE_PATTERNS:
            count = text.count(pattern)
            if count:
                findings.append(Finding(path, pattern, count))
    return findings


def command_read(args: argparse.Namespace) -> int:
    paths = resolve_patterns(args.target)
    if not paths:
        print("CODEX-UTF8-READ status=fail reason=no-matches", file=sys.stderr)
        return 2
    for index, path in enumerate(paths):
        if len(paths) > 1:
            if index:
                print()
            print(f"--- {rel(path)}")
        print(read_file(path, args.first, args.last), end="")
    return 0


def command_list(args: argparse.Namespace) -> int:
    paths = resolve_patterns(args.target)
    for path in paths:
        print(rel(path))
    print(f"CODEX-UTF8-LIST status=pass files={len(paths)}")
    return 0


def command_scan(args: argparse.Namespace) -> int:
    findings = scan_controlled_files()
    status = "pass" if not findings else "fail"
    print(
        f"CODEX-UTF8-GUARD status={status} "
        f"files={len(candidate_text_files())} findings={len(findings)}"
    )
    if args.summary_line:
        return 0 if not findings else 2
    for item in findings:
        escaped = item.pattern.encode("unicode_escape").decode("ascii")
        print(f"FAIL {rel(item.path)} pattern={escaped} count={item.count}")
    return 0 if not findings else 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "UTF-8-safe project I/O for Codex. Prefer ASCII globs so PowerShell "
            "does not corrupt Chinese paths before Python receives them."
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)

    read = sub.add_parser("read")
    read.add_argument("target", nargs="+", help="Path or glob, preferably ASCII-only.")
    read.add_argument("--first", type=int)
    read.add_argument("--last", type=int)
    read.set_defaults(func=command_read)

    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("target", nargs="+", help="Path or glob, preferably ASCII-only.")
    list_cmd.set_defaults(func=command_list)

    scan = sub.add_parser("scan")
    scan.add_argument("--summary-line", action="store_true")
    scan.set_defaults(func=command_scan)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
