"""AC-1:对现有 skill 解压树跑 pack,输出 testzip 通过且文件条目集合与原 zip 逐条相等。

复现 D-055 的守恒校验。只读 完稿/,写只落临时目录(工作区外的系统 temp)。
"""
import sys
import zipfile
import tempfile
import types
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from skillctl import pkglib, cmd_pack, catalog  # noqa: E402

LIB = catalog.LIB_ROOT
SAMPLE_ZIP = LIB / "N140 架构与边界设计" / "041-module-boundary-identification.zip"


def _extract(zip_path: Path, dest: Path) -> Path:
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(dest)
    # 顶层目录
    top = pkglib.skill_name_from_zip(zip_path)
    return dest / top


def run_ac1() -> bool:
    assert SAMPLE_ZIP.exists(), f"缺样本 zip:{SAMPLE_ZIP}"
    orig_files = pkglib.read_zip_file_entries(SAMPLE_ZIP)
    print(f"原 zip 文件条目数(不含目录)= {len(orig_files)}")

    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        skill_dir = _extract(SAMPLE_ZIP, tdp / "unpacked")
        out_zip = tdp / "repacked.zip"

        args = types.SimpleNamespace(
            src_dir=str(skill_dir), out=str(out_zip),
            baseline=str(SAMPLE_ZIP), declare=None, no_dirs=False,
        )
        rc = cmd_pack.run(args)
        print(f"pack 退出码 = {rc}")
        if rc != 0:
            return False

        # 独立复核:重打包的文件条目集合 == 原 zip 文件条目集合
        new_files = pkglib.read_zip_file_entries(out_zip)
        if new_files != orig_files:
            print("FAIL:文件条目集合不一致")
            print("  仅原有:", sorted(orig_files - new_files))
            print("  仅新有:", sorted(new_files - orig_files))
            return False
        # 独立复核:testzip
        with zipfile.ZipFile(out_zip) as z:
            if z.testzip() is not None:
                print("FAIL:testzip 坏")
                return False
        print(f"PASS:{len(new_files)} 文件条目逐条相等 + testzip OK")
        return True


def run_ac1_negative() -> bool:
    """负例:故意删一个文件后重打,守恒必须报失败(退出码 1)。"""
    orig_files = pkglib.read_zip_file_entries(SAMPLE_ZIP)
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        skill_dir = _extract(SAMPLE_ZIP, tdp / "unpacked")
        # 删掉一个 reference 文件模拟"打包丢文件"
        victim = next(skill_dir.rglob("checklist.md"))
        victim.unlink()
        out_zip = tdp / "repacked_missing.zip"
        args = types.SimpleNamespace(
            src_dir=str(skill_dir), out=str(out_zip),
            baseline=str(SAMPLE_ZIP), declare=None, no_dirs=False,
        )
        rc = cmd_pack.run(args)
        ok = (rc == 1) and (not out_zip.exists())
        print(f"负例退出码={rc}(期望1),半成品已删={not out_zip.exists()} → {'PASS' if ok else 'FAIL'}")
        return ok


if __name__ == "__main__":
    a = run_ac1()
    print("---")
    b = run_ac1_negative()
    print("=== AC-1", "全部 PASS" if (a and b) else "有 FAIL", "===")
    sys.exit(0 if (a and b) else 1)
