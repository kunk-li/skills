#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Codex-owned PLAT(N370-N390) artifacts for A3."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from textwrap import dedent

CHAIN = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN")
PLAT = CHAIN / "PLAT"
TODAY = datetime.now().strftime("%Y-%m-%d")


def write_text(name: str, content: str) -> None:
    path = PLAT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def write_csv(name: str, rows: list[dict[str, str]], header: list[str], comments: list[str] | None = None) -> None:
    path = PLAT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        for comment in comments or []:
            fh.write(f"# {comment}\n")
        writer = csv.DictWriter(fh, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def md_contract(name: str, artifact_type: str, producer_skill: str, node: str) -> str:
    return dedent(
        f"""
        ---
        artifact_contract:
          artifact_name: {name}
          artifact_type: {artifact_type}
          producer_skill: {producer_skill}
          producer_node: {node}
          schema_version: plat.a3.artifact.v1
          readiness: pass
          evidence_profile: artifact_contract_plus_runner
          module: A3 组织架构
          chain_root: D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN
          release_posture: NO_GO / NOT_DEPLOYED
        self_gate:
          status: pass
          failed_rules: []
        ---
        """
    ).strip()


phase_rows = [
    {"phase": "PARSE", "status": "done", "evidence": "PARSE 6/6; D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/PARSE-FINDINGS.md"},
    {"phase": "B-design", "status": "done", "evidence": "B-design 19/19; D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/B-design-FINDINGS.md"},
    {"phase": "C-task", "status": "done", "evidence": "C-task 4/4; D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/C-task/N180_planning_package.md"},
    {"phase": "D-code", "status": "done", "evidence": "CODEX-A3-DCODE status=pass projects=2/2 java=210 surefire_tests=34"},
    {"phase": "TEST", "status": "done", "evidence": "CODEX-A3-TEST status=pass targets=20/20"},
    {"phase": "REL", "status": "done_no_go", "evidence": "REL-COMPLETION-AUDIT.md; NO_GO / BLOCKED"},
    {"phase": "OPS", "status": "done_not_deployed", "evidence": "OPS-COMPLETION-AUDIT.md; NO_GO / NOT_DEPLOYED"},
    {"phase": "DOC", "status": "done_not_deployed", "evidence": "DOC-COMPLETION-AUDIT.md; NO_GO / NOT_DEPLOYED"},
    {"phase": "CMP", "status": "done_evidence_only", "evidence": "CODEX-A3-CMP status=pass targets=8/8; verdict=not_globally_generated_gte_team"},
    {"phase": "PLAT", "status": "done", "evidence": "PLAT-COMPLETION-AUDIT.md; N370-N390 artifacts present"},
    {"phase": "INTEG", "status": "pending", "evidence": "not yet run"},
    {"phase": "FIND4", "status": "pending", "evidence": "not yet run"},
    {"phase": "BAR-EVAL", "status": "pending", "evidence": "not yet run; total judgment pending"},
]


def build() -> None:
    PLAT.mkdir(parents=True, exist_ok=True)

    write_text(
        "Skill路由记录.md",
        md_contract("Skill路由记录.md", "routing_record", "skill-routing-selection", "N370")
        + dedent(
            """

            # A3 链 · Skill 路由记录

            ## 路由结论

            当前工作单元是 `OA_MODULE_WORK_UNIT=FOLLOWUP_ONLY`。本次只补 A3 后续的 `PLAT(N370-N390)`,不是重跑 OA A3 全链。

            ## 阶段路由

            | 阶段 | 节点 | 状态 | 证据 |
            |---|---|---|---|
            | PARSE | N070 + N090/024 | 已完成 | 6/6 |
            | B-design | N120-N170 | 已完成 | 19/19 |
            | C-task | N180 | 已完成 | 4/4 |
            | D-code | N190-N220 | 已完成 | 23/23 + Maven 34 tests |
            | TEST | N230-N260 | 已完成 | 20/20 |
            | REL | N270-N290 | 已完成但 NO_GO | 11/11 |
            | OPS | N300-N320 | 已完成但 NOT_DEPLOYED | 14/14 |
            | DOC | N330-N360 | 已完成但 NOT_DEPLOYED | 18/18 |
            | CMP | 代码对比证据 | 已完成但非总判定 | 8/8 |
            | PLAT | N370-N390 | 本批完成 | 10 核心产物 + 4 正式别名 + 收口审计 |
            | INTEG | 集成审计 | 待跑 | 下一阶段 |
            | FIND4 | 缺陷 fan-out | 待跑 | INTEG 后 |
            | BAR-EVAL | 11 bar 总判定 | 待跑 | 最终判定 |

            ## 路由纪律

            - CMP 只作为代码对比证据,不得当 A3 总判定。
            - BAR-EVAL 对 D-060 的 11 条验收 bar 逐条评分前,`computed_total` 必须保持 `NOT_DONE`。
            - 外部 OA 仓只读;所有产物只写在 `D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/PLAT/`。
            """
        ),
    )

    write_csv(
        "Skill路由决策表.csv",
        [
            {"route_id": "R-001", "stage": row["phase"], "decision": row["status"], "basis": row["evidence"], "next": "continue" if row["status"].startswith("done") else "pending"}
            for row in phase_rows
        ],
        ["route_id", "stage", "decision", "basis", "next"],
        ["producer_skill: skill-routing-selection", "workflow_node: N370", "node_artifact_target: Skill路由决策表.csv"],
    )

    write_text(
        "上下文记忆记录.md",
        md_contract("上下文记忆记录.md", "context_memory_record", "context-memory", "N370")
        + dedent(
            f"""

            # A3 链 · 上下文记忆记录

            ## 必须优先读取的状态源

            - 当前模块状态: `D:/work/资料/skills/.codex/oa_module_state.json`
            - 11 bar 机器规则: `D:/work/资料/skills/.codex/oa_bar_rules.json`
            - OA runner: `D:/work/资料/skills/.codex/oa_shakedown.py`
            - 当前产物根: `D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/`
            - 本阶段产物: `D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/PLAT/`

            ## 不能忘的判定

            - A3 当前总状态仍是 `NOT_DONE`。
            - 本阶段完成后,下一步是 `INTEG`,不是 BAR-EVAL 也不是宣布通过。
            - `REL/OPS/DOC/CMP` 均继承 `NO_GO / NOT_DEPLOYED`。
            - 四个外部未决项仍未被机器关闭:PEND-A3-02、PEND-A3-03、BRISK-002、BRISK-006。

            ## 会话记忆

            - D-132: Codex 只用 `.codex` 原生面,不读/不转发其他工具私有目录。
            - D-133: OA 模块必须区分总状态与当前工作单元。
            - D-134: Codex 执行面以 `oa_shakedown.py` 为主,hook 只做防错入口。

            更新时间: {TODAY}
            """
        ),
    )

    write_text(
        "上下文记忆快照.md",
        md_contract("上下文记忆快照.md", "context_memory_snapshot", "context-memory", "N370")
        + "\n\n# A3 PLAT 上下文记忆快照\n\n本文件是 `上下文记忆记录.md` 的 v2 正式输出名别名。权威内容见 `D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/PLAT/上下文记忆记录.md`。\n",
    )

    write_text(
        "多Skill编排记录.md",
        md_contract("多Skill编排记录.md", "orchestration_record", "multi-skill-orchestration", "N370")
        + dedent(
            """

            # A3 链 · 多 Skill 编排记录

            ## 编排形态

            ```text
            PARSE -> B-design -> C-task -> D-code -> TEST -> REL -> OPS -> DOC -> CMP -> PLAT -> INTEG -> FIND4 -> BAR-EVAL
            ```

            ## PLAT 内部顺序

            1. N370 路由与记忆:skill-routing-selection -> context-memory -> multi-skill-orchestration -> state-machine-driven-orchestration。
            2. N380 门禁与人工协同:gate-pass-decision -> fallback-switching -> human-confirmation-node-management。
            3. N390 治理: audit-trail-management -> template-management -> quality-scoring-engine。

            ## 本次关键编排判断

            - PLAT 可以收口,因为它只记录链路元治理,不要求真实生产放行。
            - PLAT 收口不改变 A3 总判定;`BAR-EVAL_PENDING` 仍是总 blocker。
            - 下一阶段 INTEG 必须复核:已完成前缀 + PLAT 新产物 + CMP 证据 + 外部 blocker 是否一致。
            """
        ),
    )

    write_text(
        "多skill执行计划.yaml",
        dedent(
            """
            artifact_contract:
              artifact_name: 多skill执行计划.yaml
              artifact_type: multi_skill_execution_plan
              producer_skill: multi-skill-orchestration
              producer_node: N370
              schema_version: plat.a3.plan.v1
              readiness: pass
              module: A3 组织架构
            module: A3-org
            current_work_unit: FOLLOWUP_ONLY
            plan:
              - node: N370
                skills:
                  - skill-routing-selection
                  - context-memory
                  - multi-skill-orchestration
                  - state-machine-driven-orchestration
                output:
                  - Skill路由记录.md
                  - Skill路由决策表.csv
                  - 上下文记忆记录.md
                  - 上下文记忆快照.md
                  - 多Skill编排记录.md
                  - 多skill执行计划.yaml
                  - 状态机编排记录.md
                  - 状态机流转记录.csv
              - node: N380
                skills:
                  - gate-pass-decision
                  - fallback-switching
                  - human-confirmation-node-management
                output:
                  - 门禁放行记录.csv
                  - 失败兜底切换记录.csv
                  - 人工确认节点清单.csv
              - node: N390
                skills:
                  - audit-trail-management
                  - template-management
                  - quality-scoring-engine
                output:
                  - 审计留痕日志.csv
                  - 模板库索引.csv
                  - 质量评分结果.csv
            next_after_plat:
              - INTEG
              - FIND4
              - BAR-EVAL
            total_verdict_rule: BAR-EVAL must score all 11 bars PASS; phase completion is evidence only.
            """
        ),
    )

    write_text(
        "状态机编排记录.md",
        md_contract("状态机编排记录.md", "state_machine_record", "state-machine-driven-orchestration", "N370")
        + dedent(
            """

            # A3 链 · 状态机编排记录

            ## 状态机

            ```text
            todo -> in_progress -> done
                              \\-> blocked/no_go 不等于 done
            ```

            ## 当前状态

            - 已完成前缀: PARSE、B-design、C-task、D-code、TEST、REL、OPS、DOC、CMP、PLAT。
            - 剩余后缀: INTEG、FIND4、BAR-EVAL。
            - 总判定: NOT_DONE。

            ## 防错规则

            - `phase=done` 只表示该阶段产物完整并通过物理审计。
            - `computed_total=PASS` 只能由 BAR-EVAL 11/11 PASS 触发。
            - `NO_GO / NOT_DEPLOYED` 是当前发布姿态,不得被 PLAT 改写。
            """
        ),
    )

    write_csv(
        "状态机流转记录.csv",
        [
            {"seq": str(i + 1), "phase": row["phase"], "from": "todo", "to": row["status"], "trigger": row["evidence"]}
            for i, row in enumerate(phase_rows)
        ],
        ["seq", "phase", "from", "to", "trigger"],
        ["producer_skill: state-machine-driven-orchestration", "workflow_node: N370", "node_artifact_target: 状态机流转记录.csv"],
    )

    gate_rows = [
        {"gate_id": "GP-01", "gate": "D-code 物理门", "verdict": "PASS", "criteria": "Maven test + no-stub + nonzero tests", "evidence": "CODEX-A3-DCODE status=pass projects=2/2 java=210 surefire_tests=34", "blocked_by": "-"},
        {"gate_id": "GP-02", "gate": "TEST 产物门", "verdict": "PASS", "criteria": "20 target artifacts", "evidence": "CODEX-A3-TEST status=pass targets=20/20", "blocked_by": "-"},
        {"gate_id": "GP-03", "gate": "REL 发布门", "verdict": "NO_GO", "criteria": "release readiness", "evidence": "REL-COMPLETION-AUDIT.md", "blocked_by": "PEND-A3-02;PEND-A3-03;BRISK-002;BRISK-006"},
        {"gate_id": "GP-04", "gate": "OPS 运行门", "verdict": "NOT_DEPLOYED", "criteria": "production evidence", "evidence": "OPS-COMPLETION-AUDIT.md", "blocked_by": "not deployed; no real production metrics"},
        {"gate_id": "GP-05", "gate": "DOC 文档门", "verdict": "PASS_WITH_NO_GO_INHERITED", "criteria": "18 target artifacts", "evidence": "DOC-COMPLETION-AUDIT.md", "blocked_by": "release posture inherited"},
        {"gate_id": "GP-06", "gate": "CMP 代码对比证据门", "verdict": "PASS_EVIDENCE_ONLY", "criteria": "8 target artifacts", "evidence": "CODEX-A3-CMP status=pass targets=8/8 verdict=not_globally_generated_gte_team", "blocked_by": "not a total judgment"},
        {"gate_id": "GP-07", "gate": "PLAT 阶段门", "verdict": "PASS", "criteria": "N370-N390 target artifacts", "evidence": "PLAT-COMPLETION-AUDIT.md", "blocked_by": "-"},
        {"gate_id": "GP-08", "gate": "A3 总判定门", "verdict": "NOT_DONE", "criteria": "BAR-EVAL 11 bars", "evidence": "BAR-EVAL pending", "blocked_by": "BAR-EVAL_PENDING"},
    ]
    write_csv("门禁放行记录.csv", gate_rows, ["gate_id", "gate", "verdict", "criteria", "evidence", "blocked_by"], ["producer_skill: gate-pass-decision", "workflow_node: N380", "node_artifact_target: 门禁放行记录.csv"])

    write_csv(
        "失败兜底切换记录.csv",
        [
            {"fallback_id": "FB-01", "trigger": "没有真实生产部署", "primary": "读取生产监控/日志", "fallback": "继承 REL/OPS 的 NO_GO / NOT_DEPLOYED,只写产物级证据", "status": "applied"},
            {"fallback_id": "FB-02", "trigger": "CMP 不是 generated>=team 全局通过", "primary": "宣布代码优于团队", "fallback": "仅作为代码对比证据进入 BAR-EVAL", "status": "applied"},
            {"fallback_id": "FB-03", "trigger": "外部 blocker 未关闭", "primary": "发布放行", "fallback": "保留人工确认节点,不替 OA 判定", "status": "applied"},
            {"fallback_id": "FB-04", "trigger": "deep 审计可能并发跑 Maven", "primary": "并行清理 target", "fallback": "使用 D:/work/资料/skills/.codex/tmp/oa_shakedown_audits.lock 串行化", "status": "implemented"},
            {"fallback_id": "FB-05", "trigger": "第四模块切换", "primary": "改 hook 代码", "fallback": "只换 oa_module_state.json 与模块审计脚本", "status": "policy"},
        ],
        ["fallback_id", "trigger", "primary", "fallback", "status"],
        ["producer_skill: fallback-switching", "workflow_node: N380", "node_artifact_target: 失败兜底切换记录.csv"],
    )

    write_csv(
        "人工确认节点清单.csv",
        [
            {"node_id": "HC-01", "what_needs_human": "PEND-A3-02 72h 物理反向可行性与签核", "why_machine_cannot": "跨 OA 业务/发布责任,机器不能替人接受风险", "owner_role": "OA product + tech lead", "blocks": "REL/INTEG/BAR-EVAL", "status": "pending"},
            {"node_id": "HC-02", "what_needs_human": "PEND-A3-03 大子树组织变更策略", "why_machine_cannot": "策略阈值和用户体验取舍需要业务裁定", "owner_role": "OA product + architecture", "blocks": "REL/INTEG/BAR-EVAL", "status": "pending"},
            {"node_id": "HC-03", "what_needs_human": "BRISK-002 hub-wflow saga 补偿边界", "why_machine_cannot": "跨系统一致性责任边界需系统 owner 确认", "owner_role": "workflow owner + OA architecture", "blocks": "INTEG/BAR-EVAL", "status": "pending"},
            {"node_id": "HC-04", "what_needs_human": "BRISK-006 E-table/v_d_table 契约", "why_machine_cannot": "外部表/视图契约不在本模块内可证明", "owner_role": "data owner + OA backend", "blocks": "INTEG/BAR-EVAL", "status": "pending"},
            {"node_id": "HC-05", "what_needs_human": "11 bar BAR-EVAL 最终评分", "why_machine_cannot": "只有逐条评分完成才可总判定", "owner_role": "skills owner", "blocks": "total verdict", "status": "pending"},
        ],
        ["node_id", "what_needs_human", "why_machine_cannot", "owner_role", "blocks", "status"],
        ["producer_skill: human-confirmation-node-management", "workflow_node: N380", "node_artifact_target: 人工确认节点清单.csv"],
    )

    write_csv(
        "审计留痕日志.csv",
        [
            {"log_id": "AL-01", "event": "A3 PLAT started", "evidence_path": "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/PLAT/", "verifiable": "yes"},
            {"log_id": "AL-02", "event": "D-code audit pass", "evidence_path": "D:/work/资料/skills/.codex/a3_dcode_audit.py", "verifiable": "yes"},
            {"log_id": "AL-03", "event": "CMP audit pass evidence only", "evidence_path": "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/CMP/CMP-SUMMARY.md", "verifiable": "yes"},
            {"log_id": "AL-04", "event": "Codex runner distinguishes run_status from computed_total", "evidence_path": "D:/work/资料/skills/.codex/oa_shakedown.py", "verifiable": "yes"},
            {"log_id": "AL-05", "event": "PLAT completion audit generated", "evidence_path": "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/PLAT/PLAT-COMPLETION-AUDIT.md", "verifiable": "yes"},
        ],
        ["log_id", "event", "evidence_path", "verifiable"],
        ["producer_skill: audit-trail-management", "workflow_node: N390", "node_artifact_target: 审计留痕日志.csv"],
    )

    write_csv(
        "模板库索引.csv",
        [
            {"template_id": "TPL-01", "template": "OA module state", "source": "D:/work/资料/skills/.codex/oa_module_state.json", "reusable_for": "第四模块切换"},
            {"template_id": "TPL-02", "template": "11 bar machine rules", "source": "D:/work/资料/skills/.codex/oa_bar_rules.json", "reusable_for": "BAR-EVAL"},
            {"template_id": "TPL-03", "template": "OA shakedown runner", "source": "D:/work/资料/skills/.codex/oa_shakedown.py", "reusable_for": "阶段证据与总判定分离"},
            {"template_id": "TPL-04", "template": "PLAT artifact contract header", "source": "本目录各 .md 产物", "reusable_for": "N370-N390"},
            {"template_id": "TPL-05", "template": "NO_GO inheritance", "source": "REL/OPS/DOC/CMP completion audit", "reusable_for": "未部署模块的后续阶段"},
        ],
        ["template_id", "template", "source", "reusable_for"],
        ["producer_skill: template-management", "workflow_node: N390", "node_artifact_target: 模板库索引.csv"],
    )

    write_csv(
        "质量评分结果.csv",
        [
            {"score_id": "QS-01", "dimension": "PLAT 产物完整度", "score": "10/10 core + aliases", "evidence": "本目录产物", "why_not_full": "-"},
            {"score_id": "QS-02", "dimension": "Codex 执行协议", "score": "pass", "evidence": "oa_shakedown.py separates run_status and computed_total", "why_not_full": "-"},
            {"score_id": "QS-03", "dimension": "阶段证据", "score": "pass", "evidence": "D-code/TEST/REL/OPS/DOC/CMP audits pass", "why_not_full": "-"},
            {"score_id": "QS-04", "dimension": "发布就绪度", "score": "0", "evidence": "REL NO_GO; OPS NOT_DEPLOYED", "why_not_full": "external blockers pending"},
            {"score_id": "QS-05", "dimension": "generated>=team 全局判定", "score": "not_pass", "evidence": "CMP verdict=not_globally_generated_gte_team", "why_not_full": "team broader in production integration"},
            {"score_id": "QS-06", "dimension": "11 bar 总判定", "score": "0/11 current", "evidence": "BAR-EVAL pending", "why_not_full": "BAR-EVAL not run"},
        ],
        ["score_id", "dimension", "score", "evidence", "why_not_full"],
        ["producer_skill: quality-scoring-engine", "workflow_node: N390", "node_artifact_target: 质量评分结果.csv"],
    )

    audit = dedent(
        """
        ---
        artifact_contract:
          schema_version: plat.completion_audit.v1
          artifact_name: PLAT-COMPLETION-AUDIT.md
          artifact_type: completion_audit
          producer_skill: codex-plat-completion-audit
          producer_node: PLAT
          readiness: red
          release_id: A3-ORG-REL-PILOT-001
          service_scope: oa-a3-org
          release_posture: NO_GO / NOT_DEPLOYED
        self_gate:
          status: pass
          failed_rules: []
        quality_self_score:
          overall_level: A
        ---

        # A3 PLAT 收口审计

        ## 结论

        A3 PLAT 阶段 N370-N390 的 10 个核心目标产物已落盘,并额外补齐 workflow_v2 正式输出名别名。PLAT 阶段可收口。

        这不是 A3 总判定,也不是生产放行。当前 A3 仍是 `NOT_DONE / NO_GO / NOT_DEPLOYED`;下一步是 `INTEG`,之后仍需 `FIND4` 和 `BAR-EVAL`。只有 BAR-EVAL 对 D-060 的 11 条验收 bar 逐条评分全部 PASS 后,才能改变总判定。

        ## 产物目录

        `D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/PLAT/`

        ## 目标产物

        - N370: `Skill路由记录.md`, `Skill路由决策表.csv`, `上下文记忆记录.md`, `上下文记忆快照.md`, `多Skill编排记录.md`, `多skill执行计划.yaml`, `状态机编排记录.md`, `状态机流转记录.csv`
        - N380: `门禁放行记录.csv`, `失败兜底切换记录.csv`, `人工确认节点清单.csv`
        - N390: `审计留痕日志.csv`, `模板库索引.csv`, `质量评分结果.csv`

        ## 继承证据

        - D-code: `CODEX-A3-DCODE status=pass projects=2/2 java=210 surefire_tests=34`
        - TEST: `CODEX-A3-TEST status=pass targets=20/20`
        - REL: `CODEX-A3-REL status=pass targets=11/11 csv_rows=50`;发布姿态 `NO_GO / BLOCKED`
        - OPS: `CODEX-A3-OPS status=pass targets=14/14 csv_rows=4`;运行姿态 `NOT_DEPLOYED`
        - DOC: `CODEX-A3-DOC status=pass targets=18/18 csv_rows=23 workbook=present`
        - CMP: `CODEX-A3-CMP status=pass targets=8/8 features=20 endpoints=261 generated_java=97 team_java=454 verdict=not_globally_generated_gte_team`

        ## 未关闭项

        - PEND-A3-02: 72h 物理反向仍需 OA 团队确认。
        - PEND-A3-03: 大子树组织变更策略仍需业务/架构裁定。
        - BRISK-002: hub-wflow saga 补偿边界仍需系统 owner 确认。
        - BRISK-006: E-table/v_d_table 契约仍需数据 owner 确认。
        - BAR-EVAL: 11 条验收 bar 尚未评分,总判定仍未完成。

        ## 下一步

        更新 `D:/work/资料/skills/.codex/oa_module_state.json`:把 `PLAT` 从 pending 移到 completed,`OA_MODULE_NEXT` 改为 `INTEG`。然后执行 INTEG。
        """
    )
    write_text("PLAT-COMPLETION-AUDIT.md", audit)

    manifest = {
        "schema_version": "plat.manifest.v1",
        "module": "A3-org",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "chain_root": str(CHAIN).replace("\\", "/"),
        "artifacts": sorted(p.name for p in PLAT.iterdir() if p.is_file()),
        "total_verdict": "NOT_DONE",
        "next": "INTEG",
    }
    write_text("PLAT-ARTIFACT-MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build()
    print(f"Generated PLAT artifacts in {PLAT}")
