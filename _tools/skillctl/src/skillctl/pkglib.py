"""公共库 (COMP-6):遍历解压树 / 读 zip 条目 / 解析 CHANGELOG 头 / 解析 SKILL frontmatter。

设计依据:02-tech-solution/SOLUTION-skillctl.md 的 S4 内部函数契约。
纯标准库,无第三方,无网络。
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

# CHANGELOG 顶部条目:  "## v4.1.0 (2026-07-02) — contract-surface inventory before stubbing"
# 破折号可能是 em-dash(—)或 hyphen,标题后随意。
_CHANGELOG_HEAD = re.compile(
    r"^##\s+v(?P<version>\d+\.\d+\.\d+)\s+\((?P<date>\d{4}-\d{2}-\d{2})\)\s*[—\-–]\s*(?P<title>.+?)\s*$",
    re.MULTILINE,
)
_SKILL_LINE = re.compile(r"^_skill:\s*(?P<skill>.+?)_\s*$", re.MULTILINE)


def read_zip_file_entries(zip_path: str | Path) -> set[str]:
    """只返回 zip 内的**文件**条目(过滤目录条目)。

    这是条目守恒比对的单位。D-055 的「24 vs 19」误报根因正是把目录条目算进来了;
    实测全库 127/157 含目录条目、30 不含,故守恒只能比文件条目。
    """
    with zipfile.ZipFile(zip_path) as z:
        return {i.filename for i in z.infolist() if not i.filename.endswith("/")}


def iter_tree_files(src_dir: str | Path):
    """遍历解压树,产出 (abs_path, arcname)。arcname 用正斜杠、以 src_dir 的名字为顶层。

    例:src_dir=.../module-boundary-identification/ →
        arcname = module-boundary-identification/references/checklist.md
    """
    src = Path(src_dir).resolve()
    top = src.name
    for p in sorted(src.rglob("*")):
        if p.is_file():
            rel = p.relative_to(src).as_posix()
            yield p, f"{top}/{rel}"


def read_changelog_head(text: str) -> dict | None:
    """解析 CHANGELOG 顶部第一条版本条目。找不到返回 None。

    返回 {version, date, title, skill?}。skill 取紧随其后的 `_skill: xxx_` 行(若有)。
    """
    m = _CHANGELOG_HEAD.search(text)
    if not m:
        return None
    out = {"version": m.group("version"), "date": m.group("date"), "title": m.group("title").strip()}
    sk = _SKILL_LINE.search(text, m.end())
    if sk:
        out["skill"] = sk.group("skill").strip()
    return out


def read_skill_meta(text: str) -> dict:
    """极简解析 SKILL.md 首个 `---...---` YAML 头,只取 name / description 两键。

    不引第三方 yaml。返回 {name?, description?, _error?}。
    description 允许单行标量;遇折叠/多行结构则只截首行并置 _multiline=True(降级 warn,不 error)。
    """
    if not text.startswith("---"):
        return {"_error": "no frontmatter block"}
    end = text.find("\n---", 3)
    if end == -1:
        return {"_error": "unterminated frontmatter"}
    head = text[3:end]
    out: dict = {}
    cur_key = None
    for line in head.splitlines():
        m = re.match(r"^(name|description):\s*(.*)$", line)
        if m:
            cur_key = m.group(1)
            val = m.group(2).strip()
            if val in ("|", ">", "|-", ">-"):
                out[cur_key] = ""
                out["_multiline"] = True
            else:
                out[cur_key] = val.strip().strip('"').strip("'")
        elif cur_key and line.startswith(" ") and out.get("_multiline") and not out.get(cur_key):
            # 折叠块的首行内容
            out[cur_key] = line.strip()
    return out


def skill_name_from_zip(zip_path: str | Path) -> str | None:
    """从 zip 顶层目录名推断 skill 英文名(顶层唯一目录)。"""
    with zipfile.ZipFile(zip_path) as z:
        tops = {n.split("/", 1)[0] for n in z.namelist() if "/" in n or n.endswith("/")}
        tops = {t for t in tops if t}
    return next(iter(tops)) if len(tops) == 1 else None


def zip_has_changelog(zip_path: str | Path) -> bool:
    """reinforced 判据:zip 内是否含 <top>/CHANGELOG.md。

    实测全库 157 中恰 19 个为真,与叙述 19/157 分毫不差。
    """
    with zipfile.ZipFile(zip_path) as z:
        return any(n.endswith("/CHANGELOG.md") for n in z.namelist())
