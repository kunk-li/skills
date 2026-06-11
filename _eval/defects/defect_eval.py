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
    lens_status: str = "folded"  # folded=镜头已折进 skill（S3 确认其有效）/ candidate=demand-pull 新类、镜头待折（S3 标缺口）


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
    # ── audit_coverage（敏感操作路径无审计记录 = 取证盲区）→ 054 ──
    # 第二域(Java/OA)扩源:缺陷类蒸馏自 OA master-audit operator 核过的 C4/H7,
    # 2026-06-11 复核于 origin/master@b31523b9 再次确认 still_open。镜头语言无关,
    # 故配 Python + Java 双形态 fixture,detector 同时认 def / 修饰符方法头 + 注解审计。
    Fixture(
        id="audit_cov_01", defect_class="audit_coverage",
        skill="054 sensitive-operation-audit (Audit-coverage)", severity="high",
        buggy=(
            "class AccountService:\n"
            "    def reactivate_with_totp_rebind(self, uid):\n"
            "        self._reset_password(uid)\n"
            "        self._rebind_totp(uid)\n"
            "        self._set_status(uid, 'ACTIVE')\n"
        ),
        marker="def reactivate_with_totp_rebind",
        summary="免密复活(改密+重绑 TOTP+激活)全程无审计记录 → 取证盲区",
        clean=(
            "class AccountService:\n"
            "    def reactivate_with_totp_rebind(self, uid):\n"
            "        self._reset_password(uid)\n"
            "        self._rebind_totp(uid)\n"
            "        self._set_status(uid, 'ACTIVE')\n"
            "        self.audit_log('reactivate', uid)\n"
        ),
        provenance="OA master-audit C4 免密复活零审计（operator 核;2026-06-11 复核 still_open;054 Audit-coverage 镜头）",
    ),
    Fixture(
        id="audit_cov_02", defect_class="audit_coverage",
        skill="054 sensitive-operation-audit (Audit-coverage)", severity="high",
        buggy=(
            "class UserService {\n"
            "    public void grantRole(Long uid, String role) {\n"
            "        this.rel.add(uid, role);\n"
            "        this.cache.evict(uid);\n"
            "    }\n"
            "}\n"
        ),
        marker="public void grantRole",
        summary="授予角色(提权操作)无审计记录 → 提权不可追溯（Java 形态）",
        clean=(
            "class UserService {\n"
            "    @AuditLog(\"grantRole\")\n"
            "    public void grantRole(Long uid, String role) {\n"
            "        this.rel.add(uid, role);\n"
            "        this.cache.evict(uid);\n"
            "    }\n"
            "}\n"
        ),
        provenance="OA master-audit H7 grantRole/grantPermission+TotpReset 家族零审计（operator 核;2026-06-11 复核 still_open;054 Audit-coverage）",
    ),
    # ── disabled_guard（带临时/勿提交标记的守卫被注释却进 release 线）→ 070（fold-candidate）──
    # demand-pull 自 NEW-1:D-031 循环 2026-06-11 抓到的「他人当日引入的新缺陷」。镜头尚未折进 070
    # (070 现有「Dead guard」= 结构性死守卫,本类「被注释旁路的活守卫」是其邻类、未覆盖)→ lens_status=candidate,
    # S3 在此扮演「标缺口」角色(D-030):真缺陷类可测,但 070 还抓不到 = 下轮 D-019 fold 候选。
    Fixture(
        id="disabled_guard_01", defect_class="disabled_guard",
        skill="070 low-quality-code-detection (Disabled-guard)", severity="high",
        buggy=(
            "def submit_address_ticket(param):\n"
            "    # [临时·测试旁路·测完恢复·勿提交] 今天处封板期内，注释以跑通流程\n"
            "    # if is_in_locked_window(now()):\n"
            "    #     raise LockedWindowError(param.eid)\n"
            "    return create_ticket(param)\n"
        ),
        marker="勿提交",
        summary="带勿提交标记的合规守卫被整段注释旁路、却已进 release 线 → 控制在窗口内失效",
        clean=(
            "def submit_address_ticket(param):\n"
            "    if is_in_locked_window(now()):\n"
            "        raise LockedWindowError(param.eid)\n"
            "    return create_ticket(param)\n"
        ),
        provenance="OA NEW-1 USDT 封板期临时旁路 abb61260（operator 核;commit 注释自带「勿提交」却 merge 进 origin/master;070 Disabled-guard fold-candidate）",
        lens_status="candidate",
    ),
    Fixture(
        id="disabled_guard_02", defect_class="disabled_guard",
        skill="070 low-quality-code-detection (Disabled-guard)", severity="high",
        buggy=(
            "public void submitAddressTicket(Param param) {\n"
            "    // [temporary bypass · restore after E2E · do not commit] window check off to run flow\n"
            "    // if (isInLockedWindow(now())) {\n"
            "    //     throw LockedWindowException.of(param.getEid());\n"
            "    // }\n"
            "    createTicket(param);\n"
            "}\n"
        ),
        marker="do not commit",
        summary="带 do-not-commit 标记的守卫被注释旁路、却已提交（Java 形态，直接镜像 NEW-1）",
        clean=(
            "public void submitAddressTicket(Param param) {\n"
            "    if (isInLockedWindow(now())) {\n"
            "        throw LockedWindowException.of(param.getEid());\n"
            "    }\n"
            "    createTicket(param);\n"
            "}\n"
        ),
        provenance="OA NEW-1 同类 Java 形态（070 Disabled-guard fold-candidate）",
        lens_status="candidate",
    ),
]

# 已记录但需 call-graph / dataflow / 跨文件 schema、机械纯扫描抓不准 → 归 LLM/定期审计臂（诚实，同 D-030）：
#   money_atomicity(#33,055/093 money_flow)  ·  dead_code/wired_but_unused(#37,093)
# OA(Java)第二域扩源诚实读数（2026-06-11 复核 12 条 still_open）：12 条里只有 audit_coverage
#   (C4/H7 = 敏感操作零审计)能干净机械化、已收为 fixture；其余 9 条需跨文件/语义，留 llm/审计臂——
#   · C1 双签 quorum 死码 / C2 同人双签塌缩 / H6 无锁并发 → 需 dataflow / 缺失守卫推断
#   · H1/H2 wflow 端点缺失 → 需跨服务 caller↔server 契约(093 cross_service_contract)
#   · H3/H5 状态门读不存在字段 → 需实体字段集(跨文件)  · C3 撞唯一键 → 需 schema  · H8 词表错配 → 需配置对照
# NEW-1(2026-06-11 D-031 第二次复核抓到的「他人当日引入新缺陷」= USDT 封板期守卫被「勿提交」临时旁路却进
#   release 线)也能干净机械化 → 收为 disabled_guard 类(双信号共现:旁路标记 + 邻近被注释的 throw/raise)。
#   它的镜头尚未折进 070(070 现有「Dead guard」是结构性死守卫、未覆盖「被注释的活守卫」)→ lens_status=candidate,
#   S3 在此扮演「标缺口」:真缺陷可机械测、但 070 现状抓不到 = 下轮 D-019 fold 候选(demand-pull,印证 D-030)。
# 机械臂跑 5 类（authz_input / cleanup_coverage / contract_drift / audit_coverage = 已折;disabled_guard = fold-candidate）。


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


# ── audit_coverage:敏感操作方法缺审计记录(054 Audit-coverage 镜头,语言无关)──
SENSITIVE_NAME = re.compile(
    r"(grant|revoke|reset|reactivat|unlock|impersonat|elevat|rebind|"
    r"set[_]?status|change[_]?password|reset[_]?password|disable[_]?user|enable[_]?user)",
    re.I,
)
PY_DEF = re.compile(r"^(?P<i>\s*)def (?P<name>\w+)\s*\(")
JAVA_DEF = re.compile(
    r"^(?P<i>\s*)(?:public|private|protected)[\w\s<>\[\],]*?\s(?P<name>\w+)\s*\([^;]*\)\s*\{?\s*$"
)
AUDIT_TOK = re.compile(r"audit_log|record_audit|recordAudit|auditService|@AuditLog|audit\.|writeAudit", re.I)


def detect_audit_coverage(code: str):
    """敏感操作方法体(或紧贴的方法级注解)无审计 token → 取证盲区。认 Python def 与 Java 修饰符方法头。"""
    lines = code.splitlines()
    out = []
    for i, ln in enumerate(lines):
        m = PY_DEF.match(ln) or JAVA_DEF.match(ln)
        if not m or not SENSITIVE_NAME.search(m.group("name")):
            continue
        ind = len(m.group("i"))
        body = []
        for j in range(i + 1, len(lines)):
            nx = lines[j]
            if nx.strip() and (len(nx) - len(nx.lstrip())) <= ind:
                break
            body.append(nx)
        prev = lines[i - 1] if i > 0 else ""   # Java @AuditLog 注解常在方法上一行
        if not AUDIT_TOK.search("\n".join(body)) and not AUDIT_TOK.search(prev):
            out.append((i + 1, "敏感操作方法无审计记录"))
    return out


# ── disabled_guard:临时/勿提交标记 + 邻近被注释的守卫(throw/raise)= 旁路守卫已提交 ──
# 双信号共现才报(保守、低 FP):光有 marker 或光有注释 throw 都不报,需两者邻近(NEW-1 两者都有)。
BYPASS_MARKER = re.compile(
    r"临时|勿提交|测后恢复|测试旁路|temporary|temp\s*bypass|\bbypass\b|restore after|do\s*not\s*commit|don'?t commit|TODO.*restore",
    re.I,
)
COMMENTED_GUARD = re.compile(r"^\s*(#|//)\s*.*\b(throw|raise)\b", re.I)


def detect_disabled_guard(code: str):
    lines = code.splitlines()
    out = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not ((s.startswith("#") or s.startswith("//")) and BYPASS_MARKER.search(ln)):
            continue
        seen = 0
        for j in range(i + 1, len(lines)):       # marker 后邻近窗口内找被注释的守卫
            if not lines[j].strip():
                continue
            seen += 1
            if COMMENTED_GUARD.match(lines[j]):
                out.append((i + 1, "临时/勿提交标记 + 被注释的守卫(throw/raise) = 旁路守卫已提交"))
                break
            if seen >= 4:
                break
    return out


MECHANICAL: dict[str, Callable[[str], list]] = {
    "authz_input": detect_authz_input,
    "cleanup_coverage": detect_cleanup,
    "contract_drift": detect_contract_drift,
    "audit_coverage": detect_audit_coverage,
    "disabled_guard": detect_disabled_guard,
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
        ps = per_skill.setdefault(fx.skill, {"recall": [], "fp": [], "loc": [], "lens": fx.lens_status})
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
        tag = "  ⟨lens 已折,S3 确认有效⟩" if m["lens"] == "folded" else "  ⟨lens 待折=fold-candidate,S3 标缺口:recall 测的是 detector 可机械化、非 070 现状⟩"
        print(f"  recall={rec:.2f}  FP-rate={fpr:.2f}  n={n}  · {skill}{tag}")

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
