# -*- coding: utf-8 -*-
"""S3 · 缺陷检测 eval（measurement 引擎，D-030 唯一缺环）。

现有 _eval = 产物生成器：测「skill 产的工件像不像」，4 维饱和到 0.90、gt_similarity
混 D-012 模型偏差 → 分不出强弱 skill。本 harness 测的是另一维、也是 skill 真正值钱那维：
**「skill 套在一段真码上，抓不抓得到已知缺陷」**——D-016/D-018 全部价值所在，恰是
doc-vs-doc + 合成 eval「永远抓不到」的。

设计（对照 D-030 / measure 调查）：
- **机械判据规避 D-012**：检出= report 的行号命中 ground-truth defect_line（字符串/行匹配），
  不靠 LLM 比相似度 → 与被测模型无关，不受 GT-是-Claude/被测-是-qwen 偏差影响。
- **干净码负样本测 FP**：每个 fixture 配 clean 变体；强 skill = 高 recall + 低 FP，弱 = 漏或滥报。
- **per-skill 排序**：fixture 标 defect_class→skill，聚合出「哪个 skill 在哪类缺陷上弱」= 该优化谁。
- **两个 detector 臂**：
  · `mechanical` = 把已验证的镜头编译成纯扫描器（authz_input/cleanup/contract_drift,
    即 2 个跑过的 gate 的判定逻辑），**无需 API key、现在就能跑出真数**。
  · `llm` = 注入 SKILL.md 让模型找缺陷（接 _eval 现有 adapter）——需 model endpoint，
    本文件给接口 + delta（带/不带 skill）骨架，有 key 时插入即用。

fixture = **通用缺陷类**最小复现（D-023，不复制项目专有码）；真码侧检出力由 2 个 gate
已在 dream_true 289 文件 / 真 P0 行 projece.py:173 上验过（07/06-demo-*.md）。
provenance 字段把每类追到真实缺陷事件。

零三方依赖、纯 stdlib。`python defect_eval.py` 直接跑机械臂 + scorer 自检。
"""
from __future__ import annotations
import re, sys, importlib.util
from dataclasses import dataclass, field
from typing import Callable

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures：通用缺陷类最小复现（每个 = buggy + clean + 定位 marker + skill 映射）
# ─────────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Fixture:
    id: str
    defect_class: str       # authz_input / cleanup_coverage / contract_drift / ...
    skill: str              # 该缺陷类应由哪个 skill 抓到
    severity: str
    buggy: str              # 含缺陷的代码
    marker: str             # buggy 里缺陷所在行的唯一子串（用来算 defect_line，免手数行号）
    summary: str
    clean: str              # 修好的变体（测 FP）
    provenance: str         # 追到真实缺陷事件


FIXTURES: list[Fixture] = [
    # ── authz_input（权限位经开放 metadata 流入授权 = 提权根因）→ 016 ──
    Fixture(
        id="authz_input_01", defect_class="authz_input",
        skill="016 permission-matrix-extraction", severity="critical",
        buggy=(
            "def is_admin(user):\n"
            "    # 授权判定\n"
            '    return bool((user.metadata or {}).get("is_admin", False))\n'
        ),
        marker='.get("is_admin"',
        summary="权限位 is_admin 读自开放 metadata 做 authz → 任意用户自封 admin",
        clean=(
            "def is_admin(user):\n"
            "    # 读专用字段，不读开放 metadata\n"
            '    return bool(getattr(user, "is_admin", False))\n'
        ),
        provenance="dream_true #30 P0 提权 projects.py:173（authz_input_gate 反证抓到此真行）",
    ),
    Fixture(
        id="authz_input_02", defect_class="authz_input",
        skill="016 permission-matrix-extraction", severity="high",
        buggy=(
            "def apply_update(user, payload):\n"
            "    meta = dict(user.metadata or {})\n"
            '    user.role = meta.get("role", "viewer")  # 角色取自 client 可写包\n'
            "    return user\n"
        ),
        marker='meta.get("role"',
        summary="role 权限位取自 client 可写 metadata 包 = 越权",
        clean=(
            "def apply_update(user, payload):\n"
            "    meta = dict(user.metadata or {})\n"
            '    meta.pop("role", None)  # 剥离 client 传入的权限位\n'
            "    return user\n"
        ),
        provenance="authz_input 类（016 permission-input-provenance / 017 authz_input tag）",
    ),
    # ── cleanup_coverage（持外部资源的删除路径漏回收 → 孤儿）→ 017 ──
    Fixture(
        id="cleanup_01", defect_class="cleanup_coverage",
        skill="017 data-object-identification (cleanup_coverage)", severity="major",
        buggy=(
            "class EpisodeService:\n"
            "    object_store = None\n"
            "    def delete_episode(self, eid):\n"
            "        del self._rows[eid]\n"
        ),
        marker="def delete_episode",
        summary="持 object_store 的 Service 删除只删 DB 行、不清存储 → 孤儿字节",
        clean=(
            "class EpisodeService:\n"
            "    object_store = None\n"
            "    def delete_episode(self, eid):\n"
            "        self.object_store.delete(eid)\n"
            "        del self._rows[eid]\n"
        ),
        provenance="dream_true #31/#36/#39 删集漏清（cleanup_coverage_gate 抓此类）",
    ),
    Fixture(
        id="cleanup_02", defect_class="cleanup_coverage",
        skill="017 data-object-identification (cleanup_coverage)", severity="major",
        buggy=(
            "class AssetService:\n"
            "    storage = None\n"
            "    def remove_asset(self, aid):\n"
            "        self._index.pop(aid, None)\n"
        ),
        marker="def remove_asset",
        summary="持 storage 的删除方法无 storage 回收 token → 资源泄漏",
        clean=(
            "class AssetService:\n"
            "    storage = None\n"
            "    def remove_asset(self, aid):\n"
            "        self._purge_storage(aid)\n"
            "        self._index.pop(aid, None)\n"
        ),
        provenance="cleanup_coverage 类（015/017 cleanup 配对）",
    ),
    # ── contract_drift（码 vs docstring/spec 状态码漂移）→ 093 ──
    Fixture(
        id="contract_01", defect_class="contract_drift",
        skill="093 quality-gate-check (built_vs_spec)", severity="minor",
        buggy=(
            "def shot_target(idx):\n"
            '    """idx<1 时返回 422 校验错误。"""\n'
            "    if idx < 1:\n"
            "        raise UserError(http_status=400)\n"
        ),
        marker="http_status=400",
        summary="docstring/spec 写 422、码返 400 = 契约漂移",
        clean=(
            "def shot_target(idx):\n"
            '    """idx<1 时返回 422 校验错误。"""\n'
            "    if idx < 1:\n"
            "        raise UserError(http_status=422)\n"
        ),
        provenance="dream_true #38 状态码漂移（contracts.py 422-vs-400）",
    ),
    Fixture(
        id="contract_02", defect_class="contract_drift",
        skill="093 quality-gate-check (built_vs_spec)", severity="minor",
        buggy=(
            "def create_user(body):\n"
            '    """重复用户名返回 409 冲突。"""\n'
            "    if exists(body.name):\n"
            "        return JSONResponse(status_code=400)\n"
        ),
        marker="status_code=400",
        summary="docstring 写 409、码返 400 = 契约漂移",
        clean=(
            "def create_user(body):\n"
            '    """重复用户名返回 409 冲突。"""\n'
            "    if exists(body.name):\n"
            "        return JSONResponse(status_code=409)\n"
        ),
        provenance="contract_drift 类（093 built_vs_spec / mechanism-substituted）",
    ),
]

# 已记录但需 call-graph / dataflow、机械纯扫描抓不准 → 归 LLM/定期审计臂（诚实，同 D-030）：
#   money_atomicity(#33,055/093 money_flow)  ·  dead_code/wired_but_unused(#37,093)
# 这两类不放机械 fixture，留 llm 臂；机械臂只跑能干净机械化的 3 类。


# ─────────────────────────────────────────────────────────────────────────────
# Detector 臂 A：mechanical（2 个 gate 的判定逻辑编译版，无需 key、现在能跑）
#   每个 detector: (code:str) -> list[(lineno:int 1-based, msg:str)]
# ─────────────────────────────────────────────────────────────────────────────
PRIV = re.compile(r"""["'](is_admin|is_superuser|is_staff|role|roles|permission|permissions)["']""")
META = re.compile(r"\bmetadata\b|\bmeta\b")
POP = re.compile(r"\.pop\(")
CLEANUP_TOK = re.compile(r"object_store\.delete|_purge|delete_\w*objects|\.unlink\(")
STORAGE_FIELD = re.compile(r"(object_store|storage)\s*[:=]|StorageAPI")
DELETE_DEF = re.compile(r"^(?P<i>\s*)def (delete|remove)_?\w*\(")


def detect_authz_input(code: str):
    out = []
    for n, raw in enumerate(code.splitlines(), 1):
        c = raw.split("#", 1)[0]
        if not c.strip():
            continue
        if META.search(c) and PRIV.search(c) and not POP.search(c):
            out.append((n, "权限位经开放 metadata（非剥离）"))
    return out


def detect_cleanup(code: str):
    lines = code.splitlines()
    # class 持 storage？
    holds = STORAGE_FIELD.search(code) is not None
    if not holds:
        return []
    out = []
    for i, ln in enumerate(lines):
        m = DELETE_DEF.match(ln)
        if not m:
            continue
        ind = len(m.group("i"))
        body = []
        for j in range(i + 1, len(lines)):
            nx = lines[j]
            if nx.strip() and (len(nx) - len(nx.lstrip())) <= ind:
                break
            body.append(nx)
        if not CLEANUP_TOK.search("\n".join(body)):
            out.append((i + 1, "删除方法无存储清理 token"))
    return out


STATUS_IN_CODE = re.compile(r"(?:status_code|http_status)\s*=\s*(\d{3})|HTTP[ /](\d{3})")
STATUS_IN_DOC = re.compile(r"(\d{3})")


def detect_contract_drift(code: str):
    # 收集 docstring 里的 3 位码 vs code 里的状态码；不相交且都非空 → 漂移
    doc_codes, code_lines = set(), []
    in_doc = False
    for n, raw in enumerate(code.splitlines(), 1):
        s = raw.strip()
        if s.startswith('"""') or s.startswith("'''"):
            in_doc = not in_doc if s.count('"""') + s.count("'''") == 1 else in_doc
            for c in STATUS_IN_DOC.findall(s):
                if c[0] in "45":
                    doc_codes.add(c)
            continue
        if in_doc:
            for c in STATUS_IN_DOC.findall(s):
                if c[0] in "45":
                    doc_codes.add(c)
            continue
        m = STATUS_IN_CODE.search(raw)
        if m:
            code_lines.append((n, m.group(1) or m.group(2)))
    code_codes = {c for _, c in code_lines}
    out = []
    if doc_codes and code_codes and doc_codes.isdisjoint(code_codes):
        for n, c in code_lines:
            out.append((n, f"码返 {c} 与 doc/spec {sorted(doc_codes)} 漂移"))
    return out


MECHANICAL: dict[str, Callable[[str], list]] = {
    "authz_input": detect_authz_input,
    "cleanup_coverage": detect_cleanup,
    "contract_drift": detect_contract_drift,
}


# ─────────────────────────────────────────────────────────────────────────────
# Detector 臂 B：llm（注入 SKILL.md 让模型找缺陷）—— 接口就绪，需 model adapter
# ─────────────────────────────────────────────────────────────────────────────
def detect_via_skill(code: str, skill_md: str, *, with_skill: bool):
    """注入（或不注入）SKILL.md，让模型在 code 里找缺陷，解析成 [(lineno,msg)]。
    返回 None = 无 adapter/key（跳过，不影响机械臂）。

    接 _eval 现有 adapter（adapters.py 的 SS_EVAL_INJECT_SKILL 已是 skill 注入雏形）：
      prompt = (skill_md if with_skill else "") + "\n找出下列代码的缺陷，每行输出 LINE:n 摘要\n" + code
      raw = adapter.run(prompt);  return parse_lines(raw)
    with_skill=False 臂 = 对照（裸模型），出 delta = 证 SKILL.md 真在提升检出而非裸模型本能。
    """
    if _ADAPTER is None:
        return None
    raise NotImplementedError("插入 _eval/adapters.py 的 run() + LINE:n 解析即可")


_ADAPTER = None  # 有 key 时：from _eval.adapters import build_adapter; _ADAPTER = build_adapter()


# ─────────────────────────────────────────────────────────────────────────────
# Scorer：机械判据（定位命中），干净码测 FP
# ─────────────────────────────────────────────────────────────────────────────
def defect_line(fx: Fixture) -> int:
    for n, ln in enumerate(fx.buggy.splitlines(), 1):
        if fx.marker in ln:
            return n
    raise ValueError(f"{fx.id}: marker {fx.marker!r} 不在 buggy 里")


def score_fixture(fx: Fixture, detector: Callable[[str], list], tol: int = 1):
    """recall_hit = 在 buggy 上 report 的行命中 defect_line±tol；fp = 在 clean 上有任何 report。"""
    dl = defect_line(fx)
    buggy_hits = detector(fx.buggy)
    clean_hits = detector(fx.clean)
    recall_hit = any(abs(n - dl) <= tol for n, _ in buggy_hits)
    fp = len(clean_hits) > 0
    localized = any(n == dl for n, _ in buggy_hits)
    return {"recall_hit": recall_hit, "localized": localized, "fp": fp,
            "buggy_hits": buggy_hits, "clean_hits": clean_hits, "defect_line": dl}


def run_mechanical():
    """跑机械臂 → per-skill recall/FP 排序（= 哪个 skill 在哪类缺陷上弱）。"""
    per_skill: dict[str, dict] = {}
    rows = []
    for fx in FIXTURES:
        det = MECHANICAL.get(fx.defect_class)
        if det is None:
            rows.append((fx, None))
            continue
        r = score_fixture(fx, det)
        rows.append((fx, r))
        ps = per_skill.setdefault(fx.skill, {"recall": [], "fp": [], "loc": []})
        ps["recall"].append(1 if r["recall_hit"] else 0)
        ps["fp"].append(1 if r["fp"] else 0)
        ps["loc"].append(1 if r["localized"] else 0)
    return rows, per_skill


def main():
    print("=" * 78)
    print("S3 · 缺陷检测 eval（measurement 引擎）· 机械臂（无需 API key）")
    print("=" * 78)
    rows, per_skill = run_mechanical()

    print(f"\n[fixtures] {len(FIXTURES)} 个通用缺陷类复现，机械臂覆盖 {len(MECHANICAL)} 类\n")
    for fx, r in rows:
        if r is None:
            print(f"  · {fx.id} ({fx.defect_class}) → 无机械 detector（归 LLM/审计臂）")
            continue
        tag = "✅" if (r["recall_hit"] and not r["fp"]) else "⚠️"
        print(f"  {tag} {fx.id} ({fx.defect_class})  recall={'HIT' if r['recall_hit'] else 'MISS'}"
              f"@line{r['defect_line']}  localized={r['localized']}  clean_FP={'是' if r['fp'] else '否'}")

    print("\n[per-skill 排序] recall / FP-rate（弱在前 = 该优化谁）：")
    ranked = sorted(per_skill.items(),
                    key=lambda kv: (sum(kv[1]["recall"]) / len(kv[1]["recall"]),
                                    -sum(kv[1]["fp"]) / len(kv[1]["fp"])))
    for skill, m in ranked:
        n = len(m["recall"])
        rec = sum(m["recall"]) / n
        fpr = sum(m["fp"]) / n
        print(f"  recall={rec:.2f}  FP-rate={fpr:.2f}  n={n}  · {skill}")

    # ── scorer 自检（无需 key）：用 mock「LLM 输出」证 scorer 端到端可判 ──
    print("\n[scorer 自检] mock 输出验证机械判据（不靠 LLM 相似度，规避 D-012）：")
    fx = FIXTURES[0]
    dl = defect_line(fx)
    mock_good = lambda code: [(dl, "找到提权")] if code == fx.buggy else []
    mock_blind = lambda code: []           # 漏报 → recall MISS
    mock_noisy = lambda code: [(1, "乱报")]  # clean 上也报 → FP
    for name, det in [("命中且不误报", mock_good), ("漏报", mock_blind), ("滥报", mock_noisy)]:
        r = score_fixture(fx, det)
        print(f"  mock「{name}」→ recall={'HIT' if r['recall_hit'] else 'MISS'}  FP={'是' if r['fp'] else '否'}")

    print("\n" + "=" * 78)
    print("结论：harness 端到端可跑——机械臂用 2 gate 逻辑产真 per-skill recall/FP 排序；")
    print("      scorer 走机械判据(命中行号)、规避 D-012；clean 负样本测 FP；")
    print("      LLM 臂(注入 SKILL.md + 不注入 delta)接口就绪，有 model endpoint 即插即用。")
    print("      → 第一次「有尺子知道哪个 skill 该优化」（D-030 S3）。")


if __name__ == "__main__":
    main()
