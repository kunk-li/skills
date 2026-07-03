"""skillctl CLI 入口 (COMP-1)。用法:python -m skillctl <sub> [args]。"""
from __future__ import annotations

import argparse
import io
import sys

from . import cmd_pack, cmd_lint, cmd_count, cmd_coverage


def _force_utf8_stdout():
    # Windows 终端默认 GBK 代码页,UTF-8 输出会乱码;强制 UTF-8。
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, io.UnsupportedOperation):
        pass


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="skillctl", description="skill 库打包/校验/覆盖 CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("pack", help="从解压树重建规范 zip + testzip + 文件条目守恒")
    pp.add_argument("src_dir")
    pp.add_argument("-o", "--out")
    pp.add_argument("--baseline", help="用作条目守恒基线的原 zip")
    pp.add_argument("--declare", help="条目清单文件(无原 zip 时的基线)")
    pp.add_argument("--no-dirs", action="store_true", help="不写目录条目")
    pp.set_defaults(func=cmd_pack.run)

    pl = sub.add_parser("lint", help="校验 SKILL.md frontmatter + CHANGELOG 版本条目")
    pl.add_argument("targets", nargs="*", help="zip 或解压目录(可省略,配 --all 扫全库)")
    pl.add_argument("--all", action="store_true", help="扫全库 完稿/N*/*.zip")
    pl.add_argument("--quiet", action="store_true", help="只显有问题的,不打印 ✓ 行")
    pl.set_defaults(func=cmd_lint.run)

    pc = sub.add_parser("count", help="磁盘 vs --expect vs 总表 CSV 三方对账")
    pc.add_argument("--expect", type=int, default=157)
    pc.add_argument("--csv", help="总表 CSV 路径(默认 docs/技能库总表.csv)")
    pc.set_defaults(func=cmd_count.run)

    pv = sub.add_parser("coverage", help="全库覆盖仪表盘(reinforced=含 CHANGELOG.md)")
    pv.add_argument("--format", choices=["table", "csv"], default="table")
    pv.add_argument("-o", "--out", help="csv 格式的输出文件")
    pv.set_defaults(func=cmd_coverage.run)

    return p


def main(argv=None) -> int:
    _force_utf8_stdout()
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
