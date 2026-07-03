"""cmd_coverage (COMP-5):全库枚举 + node/macro 归属 + 版本 + reinforced 标记 + 覆盖率。

reinforced = zip 含 CHANGELOG.md(实测 19/157,与叙述吻合)。
版本 = CHANGELOG 顶部条目(无 CHANGELOG 则空)。
"""
from __future__ import annotations

import csv as csvmod
import os
import zipfile

from . import catalog, pkglib


def _collect_rows() -> list[dict]:
    rows = []
    for zp in catalog.iter_library_zips():
        name = pkglib.skill_name_from_zip(zp) or os.path.splitext(os.path.basename(zp))[0]
        node = catalog.node_of_path(zp)
        macro = catalog.macro_of_node(node)
        reinforced = pkglib.zip_has_changelog(zp)
        version = ""
        if reinforced:
            with zipfile.ZipFile(zp) as z:
                cl = next((n for n in z.namelist() if n.endswith("/CHANGELOG.md")), None)
                if cl:
                    head = pkglib.read_changelog_head(z.read(cl).decode("utf-8", "replace"))
                    if head:
                        version = "v" + head["version"]
        rows.append({
            "file": os.path.basename(zp), "name": name, "node": node or "?",
            "macro": macro, "version": version, "reinforced": "Y" if reinforced else "",
        })
    return rows


def run(args) -> int:
    rows = _collect_rows()
    total = len(rows)
    reinforced = sum(1 for r in rows if r["reinforced"] == "Y")
    pct = (reinforced / total * 100) if total else 0.0

    if args.format == "csv":
        out = args.out or None
        f = open(out, "w", encoding="utf-8", newline="") if out else None
        import sys
        w = csvmod.writer(f or sys.stdout)
        w.writerow(["file", "name", "node", "macro", "version", "reinforced"])
        for r in rows:
            w.writerow([r["file"], r["name"], r["node"], r["macro"], r["version"], r["reinforced"]])
        if f:
            f.close()
            print(f"[coverage] 写出 CSV → {out}")
    else:
        print(f"{'节点':<6}{'强化':<5}{'版本':<9}skill")
        print("-" * 70)
        for r in rows:
            mark = "●" if r["reinforced"] == "Y" else "·"
            print(f"{r['node']:<6}{mark:<5}{r['version']:<9}{r['name']}")

    print("-" * 70)
    print(f"[coverage] 真强化(含 CHANGELOG.md) = {reinforced}/{total} = {pct:.1f}%")
    # 按 macro 桶汇总
    buckets: dict[str, list[int]] = {}
    for r in rows:
        b = buckets.setdefault(r["macro"], [0, 0])
        b[1] += 1
        if r["reinforced"] == "Y":
            b[0] += 1
    print("[coverage] 按 macro 桶:")
    for macro, (rf, tot) in sorted(buckets.items()):
        print(f"    {macro:<28} {rf}/{tot}")
    return 0
