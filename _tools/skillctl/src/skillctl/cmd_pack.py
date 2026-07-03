"""cmd_pack (COMP-2):从解压树重建规范 zip + testzip + 文件条目守恒。

设计依据:SOLUTION-skillctl.md S3/S4/S6。
规范格式(逆向现有库实测):文件 DEFLATED、目录条目 STORED、路径正斜杠、顶层=目录名。
守恒:只比**文件**条目集合 vs 基线(原 zip 优先,否则 --declare 清单)。
红线:默认输出到工作区/显式 -o,绝不原地覆盖 完稿/ 的 zip。
"""
from __future__ import annotations

import zipfile
from pathlib import Path

from . import pkglib


def _emit_zip(src_dir: Path, out_path: Path, with_dir_entries: bool = True) -> set[str]:
    """把 src_dir 打成规范 zip,返回写入的文件条目集合。"""
    files = list(pkglib.iter_tree_files(src_dir))
    written_files: set[str] = set()
    seen_dirs: set[str] = set()
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for abs_path, arcname in files:
            if with_dir_entries:
                # 逐级补目录条目(STORED),贴现有库多数格式
                parts = arcname.split("/")[:-1]
                acc = ""
                for part in parts:
                    acc = f"{acc}{part}/"
                    if acc not in seen_dirs:
                        zi = zipfile.ZipInfo(acc)
                        zi.compress_type = zipfile.ZIP_STORED
                        z.writestr(zi, b"")
                        seen_dirs.add(acc)
            z.write(abs_path, arcname, compress_type=zipfile.ZIP_DEFLATED)
            written_files.add(arcname)
    return written_files


def _load_baseline(baseline: str | None, declare: str | None) -> set[str] | None:
    if baseline:
        return pkglib.read_zip_file_entries(baseline)
    if declare:
        lines = Path(declare).read_text(encoding="utf-8").splitlines()
        return {ln.strip() for ln in lines if ln.strip()}
    return None


def run(args) -> int:
    src = Path(args.src_dir).resolve()
    if not src.is_dir():
        print(f"[pack] 错误:源目录不存在或非目录 — {src}")
        return 2
    if not any(src.iterdir()):
        print(f"[pack] 错误:源目录为空 — {src}")
        return 2

    out = Path(args.out).resolve() if args.out else src.parent / f"{src.name}.zip"

    # 红线:禁止写入 完稿/ 基线区
    if "完稿" in out.parts or "完稿" in str(out):
        print(f"[pack] 拒绝:输出落在只读基线区 完稿/ — {out}(红线,改用 -o 指向工作区)")
        return 2

    # 基线:未显式给 --baseline 时,若同名 zip 已存在于 src 同级则自动取作基线
    baseline = args.baseline
    if not baseline and not args.declare:
        cand = src.parent / f"{src.name}.zip"
        if cand.exists() and cand.resolve() != out:
            baseline = str(cand)

    expected = _load_baseline(baseline, args.declare)

    written = _emit_zip(src, out, with_dir_entries=not args.no_dirs)

    # testzip
    with zipfile.ZipFile(out) as z:
        bad = z.testzip()
    if bad is not None:
        out.unlink(missing_ok=True)
        print(f"[pack] 失败:testzip CRC 坏于 {bad},已删半成品")
        return 1

    # 文件条目守恒
    if expected is not None:
        missing = expected - written
        extra = written - expected
        if missing or extra:
            out.unlink(missing_ok=True)
            print(f"[pack] 失败:文件条目不守恒(基线={baseline or args.declare})")
            if missing:
                print(f"  丢失 {len(missing)} 条:")
                for m in sorted(missing):
                    print(f"    - {m}")
            if extra:
                print(f"  多出 {len(extra)} 条:")
                for e in sorted(extra):
                    print(f"    + {e}")
            print("  已删半成品。")
            return 1
        print(f"[pack] 条目守恒 OK:{len(written)} 个文件条目与基线一致")
    else:
        print(f"[pack] 无基线(未给 --baseline/--declare),仅 testzip:{len(written)} 个文件条目")

    print(f"[pack] testzip OK → {out}")
    return 0
