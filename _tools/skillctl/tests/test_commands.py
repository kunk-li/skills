"""lint / count / coverage 的测试。

测试点按 N230/080 test-point-generation 的方法从 PRD 的 AC-2/3/4 推导,
覆盖 正常 / 边界(082) / 异常(083)三类。纯脚本,无 pytest 依赖。
只读 完稿/,负例用系统 temp 合成夹具,写不落工作区外的项目资产。
"""
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from skillctl import cmd_lint, cmd_count, cmd_coverage, catalog  # noqa: E402

LIB = catalog.LIB_ROOT
SKILL_041 = LIB / "N140 架构与边界设计" / "041-module-boundary-identification.zip"

_RESULTS = []


def check(name, cond, detail=""):
    _RESULTS.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail and not cond else ""))


def _mk_skill_dir(base: Path, name: str, skill_md: str | None, changelog: str | None) -> Path:
    d = base / name
    d.mkdir(parents=True)
    if skill_md is not None:
        (d / "SKILL.md").write_text(skill_md, encoding="utf-8")
    if changelog is not None:
        (d / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
    return d


GOOD_SKILL = "---\nname: %s\ndescription: a valid one-line description here.\n---\n# body\n"
GOOD_CL = "# CHANGELOG\n\n## v1.0.0 (2026-07-03) — first\n\n_skill: %s_\n\n### Added\n- x\n"


# ---------- AC-2:lint ----------
def test_lint():
    print("AC-2 lint:")
    # TP1 正常:真 041 zip 无 error
    issues = cmd_lint._lint_one(str(SKILL_041))
    check("lint.正常/041无error", not any(l == "error" for l, _ in issues), str(issues))

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        # TP2 异常:缺 description
        d2 = _mk_skill_dir(base, "no-desc", "---\nname: no-desc\n---\n# b\n", None)
        i2 = cmd_lint._lint_one(str(d2))
        check("lint.异常/缺description报error", any("description" in m and l == "error" for l, m in i2), str(i2))

        # TP3 异常:缺 SKILL.md
        d3 = _mk_skill_dir(base, "no-skill", None, None)
        i3 = cmd_lint._lint_one(str(d3))
        check("lint.异常/缺SKILL.md报error", any(l == "error" for l, _ in i3), str(i3))

        # TP3b 边界:description 超 25 词 → warn(库 ≤25 词标准门)
        long_desc = "word " * 40  # 40 词
        d3b = _mk_skill_dir(base, "long-desc", f"---\nname: long-desc\ndescription: {long_desc}\n---\n# b\n", None)
        i3b = cmd_lint._lint_one(str(d3b))
        check("lint.边界/超25词description报warn",
              any(l == "warn" and "词数" in m for l, m in i3b), str(i3b))

        # TP4 异常:CHANGELOG 存在但格式坏
        d4 = _mk_skill_dir(base, "bad-cl", GOOD_SKILL % "bad-cl", "# CHANGELOG\n\n随便写的没版本条目\n")
        i4 = cmd_lint._lint_one(str(d4))
        check("lint.异常/坏CHANGELOG报error", any(l == "error" for l, _ in i4), str(i4))

        # TP5 边界:合规 SKILL 且无 CHANGELOG(未强化)→ 不算 error
        d5 = _mk_skill_dir(base, "no-cl", GOOD_SKILL % "no-cl", None)
        i5 = cmd_lint._lint_one(str(d5))
        check("lint.边界/无CHANGELOG不报error", not any(l == "error" for l, _ in i5), str(i5))

        # TP6 正常:全合规 → 零 issue
        d6 = _mk_skill_dir(base, "perfect", GOOD_SKILL % "perfect", GOOD_CL % "perfect")
        i6 = cmd_lint._lint_one(str(d6))
        check("lint.正常/全合规零issue", i6 == [], str(i6))


# ---------- AC-3:count 归一逻辑 ----------
def test_count_norm():
    print("AC-3 count 名字归一:")
    check("count._norm剥数字前缀", cmd_count._norm("143-skill-routing-selection") == "skill-routing-selection")
    check("count._norm无前缀不变", cmd_count._norm("data-flow-mapping") == "data-flow-mapping")
    check("count._norm空值安全", cmd_count._norm("") == "" and cmd_count._norm(None) == "")


# ---------- AC-4:coverage ----------
def test_coverage():
    print("AC-4 coverage:")
    rows = cmd_coverage._collect_rows()
    check("coverage.157行", len(rows) == 157, f"实际 {len(rows)}")
    reinforced = [r for r in rows if r["reinforced"] == "Y"]
    check("coverage.reinforced=19", len(reinforced) == 19, f"实际 {len(reinforced)}")
    check("coverage.每个reinforced都有版本", all(r["version"].startswith("v") for r in reinforced),
          str([r["name"] for r in reinforced if not r["version"]]))
    # macro 桶求和 == 157(无遗漏)
    from collections import Counter
    c = Counter(r["macro"] for r in rows)
    check("coverage.macro桶求和=157", sum(c.values()) == 157, str(dict(c)))
    check("coverage.node全部解析出", all(r["node"] != "?" for r in rows),
          str([r["file"] for r in rows if r["node"] == "?"][:5]))


def test_lint_all():
    print("lint --all 全库模式:")
    import types
    args = types.SimpleNamespace(targets=[], all=True, quiet=True)
    rc = cmd_lint.run(args)
    # 库当前 153/157 干净、0 error → 退出码 0(warn 不致 error)
    check("lint.--all退出码0(无error级)", rc == 0, f"rc={rc}")
    # --all 无目标但也不传 targets 时应枚举到 157
    check("lint.--all枚举全库157", len(list(catalog.iter_library_zips())) == 157)


if __name__ == "__main__":
    test_lint()
    test_lint_all()
    test_count_norm()
    test_coverage()
    print("=" * 50)
    passed = sum(1 for _, ok, _ in _RESULTS if ok)
    total = len(_RESULTS)
    fails = [n for n, ok, _ in _RESULTS if not ok]
    print(f"总计 {passed}/{total} PASS" + (f" · 失败:{fails}" if fails else " · 全绿"))
    sys.exit(0 if passed == total else 1)
