"""cmd_count (COMP-4):磁盘 zip 数 vs --expect vs 总表 CSV 行数,三方对账。

如实列差集,不"修正"任何一方(治 idea-seed 痛点 5:157 vs 154 从未对账)。
"""
from __future__ import annotations

import re

from . import catalog, pkglib

_PREFIX = re.compile(r"^\d+-")


def _norm(name: str) -> str:
    """归一 skill 英文名:剥前导数字前缀(如 143-)。

    磁盘顶层目录名可能带 `\\d+-` 前缀而 CSV 英文名不带——不剥则同一 skill 被两边
    各算作"独有",把命名差异虚报成缺口(2026-07-03 code review 揪出的真 bug)。
    """
    return _PREFIX.sub("", (name or "").strip())


def run(args) -> int:
    zips = list(catalog.iter_library_zips())
    disk = len(zips)
    rows = catalog.load_master_csv(args.csv) if args.csv else catalog.load_master_csv()
    csv_rows = len(rows)
    expect = args.expect

    print(f"[count] 磁盘 zip 数        = {disk}")
    print(f"[count] 总表 CSV 数据行数  = {csv_rows}")
    if expect is not None:
        print(f"[count] 期望值 --expect    = {expect}")

    # 差集:磁盘上的英文名 vs CSV 里的英文名(先剥数字前缀归一,避免虚报)
    disk_names = {_norm(pkglib.skill_name_from_zip(z) or _stem(z)) for z in zips}
    csv_names = {_norm(r.get("技能名称 英文") or "") for r in rows}
    csv_names.discard("")

    only_disk = disk_names - csv_names
    only_csv = csv_names - disk_names

    consistent = True
    if expect is not None and disk != expect:
        consistent = False
        print(f"[count] ✗ 磁盘 {disk} ≠ 期望 {expect}")
    if disk != csv_rows:
        consistent = False
        print(f"[count] ✗ 磁盘 {disk} ≠ CSV {csv_rows}(差 {disk - csv_rows})")
    if only_disk:
        print(f"[count] 仅在磁盘、不在 CSV 的 {len(only_disk)} 个:")
        for n in sorted(only_disk):
            print(f"    disk-only: {n}")
    if only_csv:
        print(f"[count] 仅在 CSV、不在磁盘的 {len(only_csv)} 个:")
        for n in sorted(only_csv):
            print(f"    csv-only : {n}")

    if consistent and not only_disk and not only_csv:
        print("[count] ✓ 三方一致")
        return 0
    return 1


def _stem(zip_path: str) -> str:
    import os
    return os.path.splitext(os.path.basename(zip_path))[0]
