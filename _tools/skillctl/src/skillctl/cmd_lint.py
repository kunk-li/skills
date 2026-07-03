"""cmd_lint (COMP-3):SKILL.md frontmatter + CHANGELOG 顶部版本条目校验。

MVP(ALT-3b):CHANGELOG 校验 = 顶部条目存在且格式合规 + `_skill:` 与目录名一致;
不做内容 diff 的 bump 检测(列入 PRD-15 后续)。
target 可为 zip 或解压目录。
"""
from __future__ import annotations

import os
import zipfile
from pathlib import Path

from . import pkglib

# description 词数上限。库自己的标准(041 CHANGELOG v4.0.0「Description trimmed to ≤25 words」);
# 实测 19 个强化包全守(14-24 词),138 未强化包普遍超标(均值 70、最长 156)。设 25 为 warn 门。
DESC_WORD_WARN = 25


def _read_targets(target: str):
    """返回 (skill_name, skill_md_text | None, changelog_text | None)。"""
    p = Path(target)
    if p.is_dir():
        name = p.name
        sk = p / "SKILL.md"
        cl = p / "CHANGELOG.md"
        return (name,
                sk.read_text(encoding="utf-8", errors="replace") if sk.exists() else None,
                cl.read_text(encoding="utf-8", errors="replace") if cl.exists() else None)
    # zip
    with zipfile.ZipFile(p) as z:
        top = pkglib.skill_name_from_zip(p)
        names = z.namelist()
        sk_n = next((n for n in names if n.endswith("/SKILL.md")), None)
        cl_n = next((n for n in names if n.endswith("/CHANGELOG.md")), None)
        return (top,
                z.read(sk_n).decode("utf-8", "replace") if sk_n else None,
                z.read(cl_n).decode("utf-8", "replace") if cl_n else None)


def _lint_one(target: str) -> list[tuple[str, str]]:
    """返回 [(level, msg)] level ∈ {error, warn}。"""
    issues: list[tuple[str, str]] = []
    name, skill_md, changelog = _read_targets(target)

    # SKILL.md
    if skill_md is None:
        issues.append(("error", "缺 SKILL.md"))
    else:
        meta = pkglib.read_skill_meta(skill_md)
        if meta.get("_error"):
            issues.append(("error", f"SKILL.md frontmatter:{meta['_error']}"))
        else:
            if not meta.get("name"):
                issues.append(("error", "SKILL.md frontmatter 缺 name"))
            elif name and meta.get("name") != name:
                issues.append(("warn", f"name({meta['name']}) 与目录名({name}) 不一致"))
            if not meta.get("description"):
                issues.append(("error", "SKILL.md frontmatter 缺 description"))
            elif len(meta["description"].split()) > DESC_WORD_WARN:
                issues.append(("warn", f"description 词数 > {DESC_WORD_WARN}"))

    # CHANGELOG(存在才校验格式;不存在只是未强化、非 error)
    if changelog is not None:
        head = pkglib.read_changelog_head(changelog)
        if head is None:
            issues.append(("error", "CHANGELOG.md 顶部无合规版本条目(需 `## vX.Y.Z (YYYY-MM-DD) — 标题`)"))
        else:
            if "skill" not in head:
                issues.append(("warn", "CHANGELOG 顶部条目后缺 `_skill: <name>_` 行"))
            elif name and head["skill"] != name:
                issues.append(("warn", f"CHANGELOG _skill_({head['skill']}) 与目录名({name}) 不一致"))
    return issues


def run(args) -> int:
    from . import catalog

    # --all:内部枚举全库,免去人肉传 157 个带空格路径(真用时暴露的缺口,2026-07-03)
    targets = list(args.targets)
    if getattr(args, "all", False):
        targets = list(catalog.iter_library_zips())
    if not targets:
        print("[lint] 无目标:给出 zip/目录,或用 --all 扫全库")
        return 2

    any_error = 0
    clean = 0
    for target in targets:
        if not os.path.exists(target):
            print(f"[lint] {target}: 路径不存在")
            any_error += 1
            continue
        issues = _lint_one(target)
        base = os.path.basename(str(target).rstrip("/\\"))
        if not issues:
            clean += 1
            if not getattr(args, "quiet", False):
                print(f"[lint] {base}: ✓ 无问题")
        else:
            for level, msg in issues:
                print(f"[lint] {base}: [{level}] {msg}")
                if level == "error":
                    any_error += 1
    if getattr(args, "all", False):
        print(f"[lint] 全库汇总:{clean}/{len(targets)} 干净,{any_error} 个 error 级问题")
    return 1 if any_error else 0
