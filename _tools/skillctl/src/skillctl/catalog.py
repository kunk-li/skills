"""catalog (COMP-7):读真库结构 + GBK 总表 CSV,提供 skill→node→macro 映射。

node 直接来自 完稿/N### 目录名(免查表)。macro 由 node 号粗分桶(D-002 的 5 路径),
桶映射是启发式,标注 confidence=coarse,不过度宣称。
"""
from __future__ import annotations

import csv
import glob
import re
from pathlib import Path


def _find_repo_root() -> Path:
    """从本文件往上走,找到含 完稿/ 的目录 = skill 库仓根。

    工具已搬进仓内(_tools/skillctl/...),自定位而非钉死绝对路径,便于整仓迁移。
    """
    for p in Path(__file__).resolve().parents:
        if (p / "完稿").is_dir():
            return p
    return Path("D:/work/资料/skills")  # 兜底:仓外历史绝对路径


REPO_ROOT = _find_repo_root()
LIB_ROOT = REPO_ROOT / "完稿"
MASTER_CSV = REPO_ROOT / "docs" / "技能库总表.csv"

# node 号 → macro 路径粗桶(依 CLAUDE.md 节点结构 + D-002)
_MACRO_BUCKETS = [
    (5, 110, "A requirement-to-prd"),
    (120, 180, "B prd-to-tech-solution"),
    (180, 190, "C solution-to-dev-tasks"),
    (190, 260, "D diff-to-pr-ready"),
    (300, 320, "E incident-to-postmortem"),
]

_NODE_RE = re.compile(r"N(\d+)")


def node_of_path(p: str | Path) -> str | None:
    """从 完稿/N140 .../xxx.zip 的路径提取 N 节点号,如 'N140'。"""
    for part in Path(p).parts:
        m = _NODE_RE.match(part)
        if m:
            return f"N{m.group(1)}"
    return None


def macro_of_node(node: str | None) -> str:
    if not node:
        return "?"
    n = int(node[1:])
    for lo, hi, name in _MACRO_BUCKETS:
        if lo <= n < hi:
            return name
    return "(其他/平台)"


def iter_library_zips():
    """产出库中每个 zip 的绝对路径(排序稳定)。"""
    yield from sorted(glob.glob(str(LIB_ROOT / "N*" / "*.zip")))


def load_master_csv(path: str | Path = MASTER_CSV) -> list[dict]:
    """读 GBK 总表 CSV(gb18030 兜底),返回 dict 行列表。"""
    p = Path(path)
    if not p.exists():
        return []
    for enc in ("gbk", "gb18030", "utf-8-sig"):
        try:
            with open(p, encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise RuntimeError(f"无法解码 CSV(试过 gbk/gb18030/utf-8-sig):{p}")
