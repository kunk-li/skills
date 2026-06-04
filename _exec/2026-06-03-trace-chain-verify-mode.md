# 执行记录 · trace-call-chain-analysis 加 `chain_completeness_verify` mode

**日期**:2026-06-03 · **关联**:D-019(优化现有不新增)/ D-018(G2 发现器模型)/ Signal #5(整条链路)

## 目标
给 N300 现有 skill `trace-call-chain-analysis` 加 `chain_completeness_verify` mode:**逐功能用 trace 验执行链(UI→请求→API→service→DB→响应→UI)是否端到端走通、断在哪**。优化现有、不新建。

## 计划(可执行步骤)
1. 读现状 — ✅
2. 设计 mode — ✅
3. 编辑 SKILL.md 加 mode — ✅
4. re-zip 回库 — ✅
5. 验证 fold 落库 — ✅
6. 记录 + 更新记忆 — ✅

---

## 执行日志

### 步1 · 读现状 ✅
- **action**:提取 `113-trace-call-chain-analysis.zip`,读 SKILL.md。
- **result**:它是 ops-runtime(N300)9-skill 家族之一,**反应式故障定位**——从 trace 重建调用链、找瓶颈/错误传播/propagation 断点,出 `Trace分析.md`。现有 mode:`critical_path`/`error_propagation`/`sampling_loss`/`latency_regression`。
- **关键发现(利好)**:它**已有**我要的核心机件——① 重建实际链 ② `propagation_gaps[]` 检测断点 ③ 缺 propagation-header → readiness red(= correlation-id 前提)④ 不完整 trace 降级规则。→ 新 mode = 在其上加"**与期望链 diff**"的主动验证框架,纯 additive。
- **约束**:9 skill 共享 `ops-runtime-shared-contract.md`,改共享契约/required 字段须 9 skill 同步 → **避开,只加 mode-specific 内容**。

### 步2 · 设计 `chain_completeness_verify` ✅
- **额外输入**:`expected_chain[]`(每功能一条有序 hop 链,来源 = `AH-`@032 / API 意图@N120 / 数据对象@N070)+ 被触发一次的该功能 trace。
- **流程**:逐功能取 expected_chain → 从 trace 重建 actual_chain → diff 每 hop(present/missing/unexpected)→ verdict:`complete` / `broken@{hop}` / `unknown`。
- **额外输出**:`chain_verification[]`(feature_id/verdict/break_point/evidence)+ `chain_coverage`(triggered/total + uncovered)。
- **realism**:验"走通"非"对"(对→测试代码 N230/N240);无 correlation → unknown+red;只覆盖被触发功能;日志路径交 sibling `log-analysis`。
- 详见落地后的 SKILL.md §chain_completeness_verify。

### 步3 · 编辑 SKILL.md ⏳
- action:additive 3 处。**result:2 处 Edit 全成** —— ① description 加 (5) proactive-verify trigger;② mode 列加 `chain_completeness_verify` + 新增完整 §段(input `expected_chain[]`、流程 diff、verdict `complete`/`broken@hop`/`unknown`、output `chain_verification[]`+`chain_coverage`、realism 纪律)。

### 步4 · re-zip 回库 ✅
- action:`Compress-Archive` 覆盖回 `完稿/N300/113-trace-call-chain-analysis.zip`。**result**:成功。

### 步5 · 验证 fold 落库 ✅
- action:expand 回的 zip + grep。**result**:`chain_completeness_verify` **命中 3 次**(mode 已落库);**库 157 zip 不变、净增 0**(D-019 兑现)。

### 步6 · 记录 + 更新记忆 ✅
- action:本记录填完;STATUS 06-03 条 + `_sessions/2026-06-03-session-1.md` 更新。**result**:done。

---

## 结论
✅ **完成**:N300 `trace-call-chain-analysis` 加 `chain_completeness_verify` mode = **「链路法」全链验证落地**,优化现有、**净增 0**。
- 验的是链**走通**,非结果**对**(对 → N230/N240 测试法)。
- **follow-up**(均优化现有,非新增):① `log-analysis` 加对应「日志法」mode(无 trace 时从 correlation-id 日志重建链)② N230 `080`/N240 `086` 「测试法」。
- 全程按「计划→执行→记录」:6 步 task + 本 `_exec` 记录。

---

## 追加(06-03)· 日志法 mode 落地(同一套 计划→执行→记录,4 步 task #7-10)
- **步1 读** `112-log-analysis.zip`:ops-runtime 同家族,reactive 日志取证;已有 correlation-id 关联 + `trace_linkage`,边界写明"链重建让位 `trace-call-chain-analysis`"。
- **步2 设计 + 步3 编辑**:加 `chain_completeness_verify`(日志法,**fallback when no trace**)—— additive 2 处(desc (5) + mode 列 & 新段)。**realism 比 trace 更严:缺日志 ≠ 断链(可能没埋点)→ `missing` 默认 `unknown`/低置信;有 trace 让位 trace skill**。
- **步4 rezip + 步5 验证**:覆盖回 `112-log-analysis.zip`;grep `chain_completeness_verify` **3 命中**;**库 157 净增 0**。
- **步6 记录**:本条 + STATUS + session。
- ✅ **链路法(trace=首选/准)+ 日志法(log=fallback/严)两 mode 均落地**。「测试法」见下。

---

## 追加(06-03)· 测试法 mode 落地(4 步 task #11-14)
- **步1 读** `086-api-test-script-generation`(N240):可执行 API 测试 bundle 生成器(pytest/k6/REST Assured…),已有 fixture/teardown/DB-schema input/`functional_mode` 副作用断言 → 全链 mode 纯 additive。
- **步2 设计 + 步3 编辑**:加 `full_chain_integration` mode —— 每功能串 request→后端→service→DB 读写→response **逐跳断言**(尤其 **DB 副作用查库**),断言源 = `AH-`@`032`。additive 3 处。
- **步4 rezip + 步5 验证**:覆盖回 `086` zip;`full_chain_integration` **3 命中**;**库 157 净增 0**。
- **realism**:产骨架+断言+fixture 计划**非 auto-绿**(接真实测试栈,video_ai 模型);UI 两端 = 浏览器 E2E 另层。

## ✅ 全链验证工具箱齐(全优化现有 · 净增 0 · 库始终 157)
| 法 | skill | 验 | 定位 |
|---|---|---|---|
| 链路 | `113 trace-call-chain-analysis` | 走通+断点 | 首选/准 |
| 日志 | `112 log-analysis` | 走通(无 trace) | fallback/严 |
| 测试 | `086 api-test-script-generation` | **结果对** | 重/确定性·进 CI |
| 静态 | `093 built_vs_spec` | 结构断链 | 最便宜/不跑 |
- 互补:trace/日志=走通(轻发现)· 测试=对(重确定性)· 静态=结构(不跑)。全程**计划→执行→记录**(14 task + 本 `_exec`)。

---

## 追加(06-03)· playbook 编排落地(4 步 task #15-18)
- **步1 读** `088-test-automation-orchestration`(N240 编排器):CI 流水编排,fail-fast 轻→重(lint→unit→integration→e2e)→ 全链 playbook 天然同构。
- **步2 设计 + 步3 编辑**:加 `full_chain_verification_playbook` mode —— 逐功能 fail-fast 串 静态(093)→走通(113/112)→对(086),聚合 `chain_verdict` 喂 093;**按 D-018:周期/上线前发现器流水,进 CI 的只是确认的确定性测试**。additive 3 处。
- **步4 rezip + 步5 验证**:`full_chain_verification_playbook` **3 命中**;**库 157 净增 0**。

## ✅✅ 全链验证闭环(本 session 总成 · 全优化现有 · 净增 0 · 库始终 157)
**6 个现有 skill 优化**:`032`(AH- 可验断言源)· `093`(静态结构断链)· `113`(链路走通)· `112`(日志走通 fallback)· `086`(全链集成测试·对)· `088`(编排 playbook 串起 093/113/112/086)。
一句话闭环:**spec 出可机械核对断言(032)→ 编排器(088)逐功能跑 静态→走通→对 → 聚合喂门禁(093);全程发现器 + 人工裁定 + 沉淀确定性测试(D-018),不当 per-PR 魔法门禁**。realism:产方法/骨架/断言,跑绿接真实栈(video_ai 模型),UI 两端另叠 E2E。

## 追加(06-03)· D-021 真用反哺折进 086(2 行,follow-up of 测试法)
- **触发**:G2(D-021)video_ai 真栈实施捡出新 prod bug(create2 `task_type` 22 字符 > `VARCHAR(20)` 生产 500)+ 结构护栏 `SETTLEMENT_WORKERS`。用户:折进 `086 full_chain_integration`。
- **执行(原子 · 隔离 `_086fold`——因 `_rehome_work` 被主线 #2 同时占用,Edit 文件态反复打架)**:extract 库 zip → 在 `full_chain_integration` 的「realism 纪律」后插「真用补充」段(① 真 DB 非 mock 才抓列宽/约束/类型 bug ② 结构护栏参数化覆盖所有 money/settlement 路径)→ `Compress-Archive -Force` 回库 → 重展验证。
- **result**:`真用补充`/`VARCHAR(20)`/`SETTLEMENT_WORKERS` 各 1 命中、`full_chain_integration mode` 仍在;**库 157 净增 0**(D-019)。已同步 D-021 + session-1。
