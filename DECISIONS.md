# Decisions · Skill Platform

> 重要决策的不可变记录。**已立的决策不要在下一个 session 里重新论证**——除非明确想推翻并写进 D-NNN-OVERRIDE。

---

## D-001 · 用 cheatsheet 5 路径作为主入口

- **日期**:2026-05-29
- **决定**:155 skill 不直接对外暴露,通过 5 条 path 入口使用
- **理由**:user 报告"不知道选哪个 skill"
- **影响**:UI / agent description / 培训材料都按 5 path 组织

## D-002 · 5 个 macro skill 对应 5 条 path

- **日期**:2026-05-29
- **决定**:固定 5 个 macro
  - A: `requirement-to-prd`
  - B: `prd-to-tech-solution`
  - C: `solution-to-dev-tasks`
  - D: `diff-to-pr-ready`
  - E: `incident-to-postmortem`
- **理由**:agent 选 4 个原子 skill 串接太难,加一层 orchestration
- **影响**:这 5 个优先实现;不在 path 里的 skill 进入"扩展库"角色
- **不复议**:Phase 3 之前不增不减

## D-003 · CinemaAI 41 工件作为 eval ground truth

- **日期**:2026-05-29
- **决定**:`_eval/tasks_cinemaai.yaml` 是主 eval 集
- **理由**:真实工件比合成任务可信 10 倍
- **影响**:tasks.yaml(25 合成)降级为 smoke test;真实 baseline 跑 cinemaai
- **风险**:CinemaAI 工件本身可能有偏(单一项目);**Phase 2 拿到 Pilot 2 数据后,扩 ground truth 集**
- **⚠️ caveat(2026-06-01,用户实战回顾)**:CinemaAI **最终 ship 的前端 UI 与 PRD 完全对不上** → 这是"部分成功",不是铁证。含义:① 别把它当 skills 的无条件成功背书 ② PRD 的 UI/交互部分作 ground truth 时尤其不可信(spec 与实际 build 脱节)③ 暴露方法论头号洞 = 无 UI 规格生成 + 无 built-vs-spec 门禁(见 STATUS Signal #4)

## D-004 · Pilot 1 = Skills Studio(自造 Pilot)

- **日期**:2026-05-29
- **决定**:不外求 Pilot,自造 internal tool
- **理由**:
  1. 公司没现成外部 Pilot 可用
  2. 自造能吃自己狗粮
  3. 风险最低(失败也不连累别人)
  4. 产物未来给 Pilot 2-3 团队当 demo
- **影响**:接下来 6 周聚焦 Skills Studio,不接其他需求
- **失败条件**:6 周内做不出 alpha → 方法论失败,**不要硬撑到 12 周**

## D-005 · Anti-goal:暂不发 Claude Skills marketplace

- **日期**:2026-05-29
- **决定**:Phase 2 之前不公开发布
- **理由**:internal 没跑通就公开发布,会被生态吐槽
- **何时复议**:Phase 2 完成判据全绿之后

## D-006 · 不做的事(回避无效循环)

- **日期**:2026-05-29
- **决定**:
  - 不再列长 task list(任务管理用 STATUS.md 的"待做"区)
  - 不再让用户在已有决策上重新选(查 DECISIONS.md 先)
  - 不再为 Phase 2 之外的事写设计文档
  - 暂不优化 path D / path E(没真实数据)
  - 暂不公开发表 skill 设计的 blog / talk
- **理由**:builder 容易陷入"思考替代执行",这条强制聚焦

## D-007 · Skill 项目记忆机制 = 这 4 份文件 + `_sessions/`

- **日期**:2026-05-29
- **决定**:
  - `CLAUDE.md`:不变的项目上下文,新 session 第一份读
  - `ROADMAP.md`:长期规划,不轻易改
  - `STATUS.md`:当前状态,每次 session 末更新
  - `DECISIONS.md`:本文件,只增不删
  - `_sessions/<date>-<n>.md`:每次 session 总结
- **理由**:跨 session 连续性需要持久化外部记忆
- **影响**:**每次 session 结束前**写 `_sessions/`,**每次 session 开始时**读 CLAUDE.md + 最近的 `_sessions/`

## D-008 · 跨 session 自动化 = SessionStart hook + Stop hook(兜底)

- **日期**:2026-05-29
- **决定**:用 Claude Code hook 把"读记忆"和"写记忆"都自动化
  - SessionStart hook(`load_memory.py`):自动注入 CLAUDE.md / STATUS.md / DECISIONS.md / 最新 _sessions/ 到新 session
  - Stop hook(`stop_check.py`):监控 STATUS.md / _sessions 是否新鲜,陈旧时通过 systemMessage + additionalContext 提醒 Claude 主动更新
  - **不依赖人的记忆**(原则:"能自动化就别让人做,人会忘")
- **理由**:跨 session 连续性 + 项目记忆维护必须自动化;依赖人或 AI 主动记得是不可靠的
- **影响**:
  - 设置在 `.claude/settings.json`(项目级)
  - 硬编码本机 Python 路径(MVP 阶段,跨机器再改)
  - Stop hook 有"6 stops 后才提醒"的保守阈值,避免每轮唠叨
- **不复议**:Phase 3 之前
- **已知不足**(等数据再改):
  - 没用 Claude Code 内置 autoMemoryEnabled(怕跟自定义机制冲突,Phase 3 再交叉验证)
  - Stop hook 只能"提醒",不能"代替"——Claude 还得自己写
  - 6 stops 阈值是猜的,真实使用后调

## D-009 · Skills Studio 工作产物目录 = `D:/projects/skills-studio/`

- **日期**:2026-06-01(session 06-01 #1)
- **决定**:Skills Studio 的工件存到 `D:/projects/skills-studio/工作产物/`,**独立于 skill 库 repo**(`D:/work/资料/skills/`)
- **理由**:
  1. Skills Studio 是 Pilot **产品**,不是 skill 库本身,物理隔离更清晰
  2. 与 CinemaAI(`D:/projects/python/ai_work/.../工作产物/`)同构,未来当 demo 一致
  3. STATUS.md 启动命令已挂此候选
- **影响**:Week 1 的 4 工件 + INDEX 已落此目录;Week 2+ 设计/代码也归此
- **不复议**:Phase 1 内

## D-010 · Skills Studio 技术栈 = Next.js + FastAPI

- **日期**:2026-06-01(session 06-01 #1)
- **决定**:前端 Next.js,后端 FastAPI(对应 PRD TD-01 / Q-01)
- **理由**:
  1. CinemaAI 已用此栈在本组织验证(13 人 ship 到 v0.1.0-alpha)
  2. `_eval/`(eval/scorers/adapters)本就是 Python → FastAPI 同进程集成 orchestrator + adapter + scorer,无跨语言开销
  3. 1 人作战复用已知栈,学习成本最低(否决更轻的 SvelteKit+Litestar)
- **约束**:**前端保持最小**(浏览 + 跑 path + 看/下工件),不做花哨 SPA,否则吞噬 6 周工时
- **影响**:Week 2 Path B 的 API/schema 按 FastAPI 设计;部署 docker-compose(Next 容器 + FastAPI 容器 + SQLite/PG 卷)
- **不复议**:Phase 1 内

## D-011 · MVP 范围 = 先 Path A 跑通,再复制 B-E

- **日期**:2026-06-01(session 06-01 #1)
- **决定**:MVP 只把 **Path A** 编排端到端跑通;Path B-E 列 STRETCH(对应 PRD TD-04 / Q-02)
- **理由**:
  1. Path A 是刚 dogfood 过、最了解产出的路径(本 session 4 工件即其产物)
  2. 编排骨架在 A 上验证通过后,B-E 主要是 prompt/config 替换,边际成本低
  3. 1 人 6 周不可能既建 5 path 编排又逐一验证
- **影响**:Week 2 Path B 只需设计**通用单-path orchestrator** + 用 A 证明;breakdown 的 F011(Path B-E)保持 STRETCH
- **不复议**:Phase 1 内

## D-012 · MVP skill 执行用免费/已有模型,不付费 Anthropic key

- **日期**:2026-06-01(session 06-01 #1)
- **决定**:Skills Studio 的 skill 调用,MVP 阶段用**免费或已有的 OpenAI-compatible 模型**(DeepSeek 默认,Qwen/GLM/Kimi 任一可),**不拿付费 Anthropic key**(对应 TD-03 / A3)
- **理由**:
  1. user 明确"先不花钱";Pilot 1 完成判据 G1-G5 不要求特定模型
  2. CinemaAI 生态已在用 DeepSeek/Qwen/Kimi/GLM,key 大概率已有
  3. 这些都是 OpenAI 兼容端点 → 只写**一个 `OpenAICompatibleAdapter`**(换 base_url+key 即切)
  4. 开发期管道用 Mock adapter(¥0),真跑切 DeepSeek(~¥1/M token,近乎免费)
- **影响**:
  - `adapters.py` 加 `OpenAICompatibleAdapter`;装 `openai` SDK(不是 anthropic)
  - PRD TD-03 / context-brief A3 / breakdown F033 已同步
  - **eval 注意**:跑 baseline 时产出模型须与 CinemaAI ground truth 对齐或重锚(D-003)——不挡 Pilot 1,可延后
- **可复议**:Phase 2 若发现质量不足以支撑 G4,再评估付费 Claude(adapter 已抽象,切换零成本)
- **实测(2026-06-01)**:DashScope 兼容端点。两档实测:
  - **qwen-plus**:单次 Path A ~6-7min,4 工件,深度足 → 超 <5min NFR
  - **qwen-turbo**:单次 **96s**(4×),质量仍达标(evidence-tag/5 层树/上游流入齐,略薄)
  - **决定:默认 qwen-turbo**(解 NFR + 省钱;plus 留"高质量"选项,改 1 行 .env 即切)→ **G4 初验通过,不需付费 Claude**;agent 模式(D-013)也不需开

## D-013 · 节点执行模式 = workflow 骨架 + 两层抽象

- **日期**:2026-06-01(session 06-01 #1)
- **决定**:Skills Studio 是 **workflow 引擎(确定性 DAG + 人工门禁),不是 agent**。节点执行抽象成两层:
  - **模型层**(D-012):Mock / OpenAICompatible(DeepSeek)/ Claude
  - **执行模式层**(本决策):`prompt_call`(MVP 默认,单次 LLM 调用 + 富上下文注入)/ `agent`(tool-use loop,质量兜底升级位)
- **理由**:
  1. SDLC 流程要确定性/可复现/门禁可控 → workflow 是对的骨架,不是 agent
  2. 但本 session 4 工件是"我作为 agent(读文件+校准)"产出的;裸调用 + 便宜模型(D-012)可能跑平庸 → 威胁 G4
  3. `prompt_call` + 富上下文(SKILL.md 全文 + 上游工件 + 格式范例)能救回大半;`agent` 预留接口,质量不够时零重构升级
- **影响**:`NodeExecutor` 两层抽象;`run_node.exec_mode` / telemetry 记 exec_mode;高价值节点(requirement-breakdown / prd-generation)优先候选 agent 升级
- **触发 agent 的判据**(TQ-03,待细化):节点 eval 分 < 阈值 或 人工标低质
- **不复议**:Phase 1 内(骨架不变;exec_mode 可按节点调)
- **实测(2026-06-01)**:qwen-plus + `prompt_call` + 富上下文,context-brief / breakdown 质量达标(evidence-tag、5 层树、上游工件正确流入)→ **agent 执行模式暂不开**(接口保留,省成本/复杂度)

## D-014 · 加"可读性层":产物必须对非 builder 可读

- **日期**:2026-06-01(session 06-01 #1)
- **触发**:真实反馈"大家不懂这是什么 / 不会用 / 看不懂结果"——**方法论正确 ≠ 人能读**;这是 G2(真用户)的头号风险
- **决定**:在方法论产物之上加一层"人话",5 件:
  1. path 大白话名("把想法写成 PRD",非 `requirement-to-prd`)
  2. 每份工件的"是什么 / 给谁看"标签(前端 map)
  3. 默认折叠契约 YAML 等机器细节(`splitFrontmatter`)
  4. **自动阅读导览**:`GET /runs/{id}/guide`(LLM 读 4 工件 → 大白话摘要,文件缓存)
  5. 首次进来 3 步引导 + "看个例子"
- **理由**:builder 脑子里有方法论,别人没有;不翻译就没人用 → north star 断在最后一公里
- **影响**:Path B-E 复用同套(标签/导览/折叠);导览用 qwen-turbo,缓存
- **验证(2026-06-01)**:导览实测产出纯大白话(无术语、逐份说关键点 + 下一步)→ "看不懂结果"缓解
- **不复议**:Phase 1 内

## D-015 · Pilot fork 拍板 = B(补 skill 头号洞);建 `ui-spec-generation`(spec↔现实验证层 1/2)

- **日期**:2026-06-01(session #4)
- **决定**:SDLC dogfood 的 A/B fork 选 **B**——补 D-003-caveat / STATUS Signal #4 记录的方法论头号洞「无 binding UI 规格 + 无 built-vs-spec 门禁」。第一件已建 = N080 **Stage-C 合成** skill `ui-spec-generation`;核心创新 = 每个 UI 组件挂一条可机械判定的 `AH-` 验收断言,使下游门禁可逐条核对 built-UI vs spec。
- **理由**:
  1. D-003-caveat 已把此洞列为「方法论头号洞」,非临时起意
  2. dogfood(真 CinemaAI 原型 + N070)证明可填,且产出 018-021 产不出的「OBJ-/SM- 绑定 + AH- 断言」层(两 gate-critical 维满分)
  3. 它直接产出 skill #2(门禁)的输入(§7 AH- 列表)
- **影响**:
  - skill #1 落 `完稿/N080 原型解析/ui-spec-generation/`;dogfood 产物 `skills-pilot/skill-fork-b/cinemaai-ui-spec-dogfood.md`
  - **skill #2(built-vs-spec 门禁)需 reality 源**;CinemaAI ship 的前端不在本机磁盘(只有 spec 侧)→ 门禁 reality feed = **RepoProbe(原 fork A)运行观测** → **A 与 B 合流**:A 从"并行选项"变为"B-gate 的现实输入"
  - 新增 skill 轻微逆"不增只减"原则——限定为这 **2 件**(generator + gate)、填实战洞,**不滚成 wholesale**(D-002 的 5-path 不增减仍守;marketplace anti-goal D-005 不碰)
- **不复议 / 边界**:**G2 真用户价值仍是更大未答题,优先级未被本决策超越**;"补验证层"止于这 2 个 skill + 其 dogfood,要再扩需新决策

## D-016 · `video_ai` = CinemaAI reality 侧;built-vs-spec 门禁在真代码上验证有效(value 实证)

- **日期**:2026-06-01(session #4)
- **事实/决定**:`D:/projects/python/ai_work/video/video_ai` 是 CinemaAI 的**真实全栈实现**(Next.js `apps/web` + FastAPI `apps/api` + Celery + Postgres,**自带 `.skills_workspace` = 团队用 skill 库建的它**)。**纠正 D-015 里"CinemaAI ship 前端不在磁盘"的错判**。`built-vs-spec-consistency-check` 以 `code-static` adapter 跑真代码 → **verdict `no_go`,5 条资金红线 fail**(失败不退款 / 失败仍扣费 / 预扣竞态 / suspended 前端不拦 / 预扣不对账),全带 file:line,3 条亲核(grep + 读源)。
- **意义**:
  1. **价值实证(最强一次)**:门禁在真 shipped 代码里抓出**会丢钱**的实现缺陷——doc-vs-doc 门禁(N100/N260/044)+ 合成 eval **永远抓不到** → 验证层有真价值,逼近 G2。
  2. **Docker reframe 定论**:`code-static` 零 Docker 即给**权威** verdict;Docker / RepoProbe-runtime **不在 spec↔现实核对的关键路径**(读代码即可);runtime adapter 留作"观测动态行为"的未来选项,非必需。
  3. **坐实 Signal #5 + D-003**:spec(N070/N120)写了 F-060-R01 同事务 / SM-PLAT-002 退款 / API-045 估价,**实现系统性丢失** → 链路保真度问题有 file:line 实锤。
- **诚实边界**:video_ai 早期 sprint(多处 `# TODO Sprint 1`),部分 fail 属"未接线"非"实现错"(预扣竞态是真 bug);**单项目单次审计**,证"门禁抓得到真 drift",**未独立证"团队带 skills ship 更快"**(完整 G2 仍欠)。
- **下一步真价值动作**:把 5 条 file:line finding **反馈 video_ai 团队**(= 真价值交付 + 天然 G2 实验),**不是再加 skill**。
- **不复议**:Docker 不再当 spec↔现实核对的前置条件。

## D-017 · 首个 G2 真人数据点(video_ai 研发裁定 + 集成测试)

- **日期**:2026-06-02
- **事实**:video_ai 缺陷清单交研发裁定 → `skill-fork-b/video_ai-defects-dev-adjudication.md`(团队跑真 Postgres 集成测试:14 passed,全量 227 passed)。7 条 = **6 真 + 1 误报**(ISSUE-3 超扣,审计已自纠)。**novel=2**(ISSUE-5 前端 suspended、ISSUE-7 80% 告警);其余 5 = 已知意图未接线(TODO/docstring/spec)。团队列 1/2/4 必修红线,同根因 = `worker:94` 完成处理器未接线(审计正确定位)。
- **对 G2 判据(≥3 novel + ≤1 误报 + 显式有用)**:误报 ✅(1 且自纠);novel ❌(2<3);有用 ~隐性是(投集成测试+修复计划),**显式未答**。
- **裁定(不美化)**:**精度高 + 真实参与**,但**低于 novelty 门槛** → 对成熟严谨团队(有 TODO/docstring/watchdog/集成测试纪律),审计价值形态 = **上线前红线巩固/核对**,非新发现。**混合偏正,非北极星铁证。**
- **双向价值(重要)**:团队**反向修正审计 3 处**——ISSUE-2 的 outbox 修法在本仓库无消费者会进 DLQ(我的 fix 会引 bug)/ ISSUE-4 双重计费被 `余额=SUM(committed+refunded)` 口径守住(我高估)/ `test_billing_race.py` 已 bitrot(我引为"正确范式"的测试本身坏了)。→ **审计长于"找 gap"、短于"开 repo-specific 药方";gate 的 fix 建议应标"待按仓库约定核"。第 3 次印证 gate finding 必过人工 verify**(P0-3 / 781 / 本次)。
- **过程教训**:差点用空模板 Write 覆盖团队已填的裁定文件(因文件已存在 Write 失败才幸免)→ 写已存在文件前必先 Read。
- **收口/不复议**:G2 还差团队对"**愿不愿在 CI/上线前跑这套核对**"的显式回答;拿到即 G2 首轮闭环。数据按实记,不美化。

## D-018 · G2 首轮闭环:built-vs-spec 门禁 = 合格的"上线前/周期性红线发现器"(非 CI 硬门禁)

- **日期**:2026-06-02
- **G2 显式价值答(来自 video_ai 实跑团队)**:**值得跑,但定位 = 周期性/上线前「发现器」+ 人工裁定 + 把确认项沉淀成确定性测试;不要做成 per-PR CI 硬门禁。**
- **理由(团队据本次数据)**:
  1. **核心价值 = 抓"该调的代码从没被调用"类缺陷**(refund/commit_charge 零调用、成功路径 TODO stub)——**普通单测天然测不到**(无法给"从未接线"的行为写断言)。spec↔code 核对正补此盲区。
  2. **最弱轴 = 定级/运行时正确性,且会"自信地错"**(唯一误报偏是最高 P0=ISSUE-3 竞态;静态推 spec↔code 不执行 → 误判 autobegin 运行时语义)。原始结论卡 CI → 非确定 + 偶发高置信误报 → flaky build + 告警疲劳 + 误修。
- **运营模型(三层 · 定)**:① **发现器**(nightly / RC 切点跑,出 file:line 报告,不卡 PR)② **裁定**(人/agent 在真实栈逐条核,不可省——定级要验)③ **沉淀**(确认项 → 快/稳/确定的测试/lint 去卡 CI,而非审计本身)。本次已产出此层 = 14 个真 PG 集成测试 + 2 条结构 guard("预扣必有结算路径"、"worker 路径不得残留 `# TODO`")。
- **价值判定**:billing 上线前一次性/周期 gate = **很值**(抓 3 个真资金红线,普通测试全漏);长期 per-commit 硬门禁 = **不值**(确认项一旦成确定性测试,审计边际价值递减)。**前提**:核查 spec 断言**收敛到红线**(F-060 资金/安全/权限)+ 显式版本化(本次 spec 自身都有 drift:POLL_TIMEOUT 30↔15,全量核噪声大)。
- **可泛化原则(平台级)**:**验证/spec↔reality 类 skill = 发现器 + 催生确定性门禁,不自任 CI 硬门禁。** 适用于 `built-vs-spec-consistency-check` 及类似。
- **G2 首轮结论**:**合格的正信号 = 北极星首个真人价值证据落地**——但限定域(高风险模块上线前核对、单模块/单项目),**非全链/全库验证**,不外推。
- **对 skill 的影响(✅ 已落 2026-06-02 → `built-vs-spec-consistency-check` SKILL.md v1.1.0)**:加「Operating model / 定位」段(discoverer 非 per-PR gate + 三层模型)、Severity 段加运行时/并发**低置信纪律**、新增「Distill→确定性门禁」段 + `distill_to_deterministic[]` 输出字段、Inputs 加 **curated versioned 红线 scope** 纪律、frontmatter + YAML `positioning` 标注。

## D-019 · 硬规则:不新增原子 skill,只优化现有 155(用户 06-02 拍板)

- **日期**:2026-06-02
- **决定**:**不再新建任何原子 skill。155 已足够。** 一切改进以**优化现有 skill** 落地(新 mode / 新输出字段 / 契约增强 / description 优化),不增条目。
- **触发**:本 session 我建了 2 个新 skill(`ui-spec-generation`@N080、`built-vs-spec-consistency-check`@N260),155→157,逆"不增只减" + D-001(条目越多越"不知道选哪个")。用户明确纠正。
- **影响**:
  - 2 个新 skill 的**已验证能力不丢**,但应 **re-home 进现有 skill**(✅ 已执行 A(2026-06-02:032→v1.1.0 加 `acceptance_hooks[]`(AH-)、093 加 `built_vs_spec` 维度、删 2 独立文件夹;库 157 zip 无重复、净增 0),见下):
    - **AH-/binding-spec 生成** → 优化 **N110 `032-acceptance-criteria-generation`**(让验收标准变成**可机械核对的 AH-** = 其本质)+ N090 `prd-generation`/N080 `018` 可 emit。**治 Signal #4 于源头**。
    - **built-vs-spec reality 核对** → 并入 **N260 `093 quality-gate-check`** 作 `built_vs_spec` 维度(带 D-018 的 discoverer-not-gate 模型),或作"使用技法"不入库。
    - 目标:净条目回 **155**。
  - **Signal #4/#5/#6 的修法一律走"优化现有 skill"**,不再催生新 skill。
- **我的 recalibration**:本 session 默认在"建/加",项目约束是"优化/减"。后续提案**先问"能否优化现有 skill 达成"**,再谈其他。
- **不复议**:Phase 3 前(同 D-002 不增不减)。

## D-020 · RepoProbe 升格为"要 ship 的真产品";build 过程 = 并发 skill 优化 + N=1 价值检验(用户 06-03 拍板)

- **日期**:2026-06-03(session #2)
- **决定**:RepoProbe 从"纯 dogfood 载体"**升格为要真建/真 ship 的产品**(重启 Docker → 补真 boot → 收窄 niche → 真 probe)。build 每一步**同时**用相应 SDLC skill,边建边优化 skill = **双赢**。
- **理由**:
  1. **本就是北极星 N=1 形态**(STATUS:Operator=1 人全栈=最小团队;价值检验="带 skills 比纯靠自己 ship 更快/更稳")。真 ship 一个产品 = 北极星本身,非偏离。
  2. **一举答两问**:① 产品能不能 ship(真 boot/真 probe)② skills 在"真要它工作"压力下暴露的弱点(比"找题材 dogfood"更真)。
  3. 用户主动拍 + RepoProbe 已有骨架(detector/sandbox/surface + Mock + 40 测试),边际成本低。
- **影响**:
  - 主线 = RepoProbe 真 build:Docker 真 boot → web repo **网络/安全命门设计**(`--network none` vs 需端口探,真冲突,必须解)→ 收窄 niche → 真 probe。
  - `工作产物/09` 优化清单从"排在 G2 后"改为**"build 中真用到就就地优化"**(用到哪个弱 skill 就地修)。
  - G2 形态 = **N=1 operator 自证**(诚实标 D-004 盲区:仍是 builder 自己;但"带 skills 更快 ship"是真数据点)。外部真用户实验(`工作产物/10` E1/E2)= 更强 G2,**不冲突、可并行**。
- **失败条件 / 何时退**:build 反复卡死(Docker 起不来 / niche 收不窄 / 安全命门无解)→ 退回 G2 外部实验,不硬撑(同 D-004 精神)。

## D-021 · G2 首个正信号兑现:验证方法在真栈上修了真红线 + 真 PG 测捡出新 prod bug

- **日期**:2026-06-03
- **事件**:用户把 built-vs-spec 审计的**资金红线** + `对` stage 测试方法,**在 video_ai 真栈上亲自实施**:
  - **修红线(设计对齐 video_gen)**:成功 = `db.begin()` 内「落库+commit」原子;失败 = 重试耗尽→退款落终态;幂等 = 聚合状态守卫 + billing `_already_settled`;`refund()` 默认退 held;结算统一放任务入口(`_run`/`_pipeline` 保持纯净可单测)。
  - **真 PG 集成测试(savepoint 回滚)捡出新 prod bug(白捡)**:`create2` 预扣 `task_type="create2_auto_narration"`(22 字符)> `billing_records.task_type` **VARCHAR(20)** → 生产提交即 **500**(整个 create2 解说功能挂)。video_gen/tts/lora 都 ≤20,create2 唯一越界。已改 `create2_narration`(17)。**列宽 bug,mock 永远测不出,真 PG 一跑现形。**
  - **验证**:8 新结算集成测试(lora/tts/create2 成败各路径)+ 22 集成 + 234 单测/4 skip + **7 结构护栏**(`MONEY_PATHS`/`SETTLEMENT_WORKERS` 参数化覆盖 video_gen+tts+lora+create2,任一 worker 退回未结算 CI 挡)——全绿。
- **意义(北极星)**:**第一个真团队 / 真栈 / 真资金红线被这套验证方法修掉,且真 PG 测捡出 mock 测不到的新 prod bug,还建了防回归护栏**。= 核心论点(**真栈验证 > doc-vs-doc + mock**;D-016 门禁找红线、D-018"对 stage 才抓运行时/数据正确性")**从断言变实证**。
- **全分层兑现一圈**:静态(审计找红线)→ 真 PG `对`(修 + 捡新 bug)→ 结构护栏(沉淀进 CI 防回归)= D-018「发现器→裁定→沉淀确定性测试」闭环,在真项目跑通。
- **诚实边界**:**实施是团队/用户做的**;我提供审计 + 方法 + 能力(skill)+ 测试骨架。本轮只修资金红线;worker 非计费 TODO(写 create2_lines/raw_video_scenes、回写 tts_url、发 outbox、触发下游)= 功能补全非丢钱,**有意留下,未动**(好的范围纪律)。
- **学习反哺(✅ 已落 086)**:① 真 DB(非 mock)才抓**列宽/约束/类型** bug → `full_chain_integration` 用真实 DB 引擎;② 结构护栏"参数化覆盖**所有** money/settlement 路径"(SETTLEMENT_WORKERS 模式)= 该进 CI 的确定性护栏。**已折进** `086` `full_chain_integration` 的「realism 纪律 · 真用补充」段(re-zip 验通:真用补充/VARCHAR(20)/SETTLEMENT_WORKERS 各 1 命中,库 157 净增 0)。

## D-022 · 验证脊(032 `AH-` → 093 `built-vs-spec`)端到端实证:能机械抓设计→实现保真度洞,且严到挡住半吊子修复

- **日期**:2026-06-03(session #2 末)
- **事件**:用 RepoProbe 自己的真洞(detector `_guess_kind` 把 Docker web 服务误判 `cli`)跑完整闭环:**032 `AH-` 从需求钉用例 → 093 `built-vs-spec` 由 3 个独立不知情子 agent 盲核** → 盲核#1 抓出 `AH-D01` fail + 2 bonus 洞 → 修 → **盲核#2 抓出我半吊子修复**(`_guess_kind` 信号没独立生效,gunicorn-only→unknown)→ 修全 → 盲核#3 **PASS**。48 单测。工件 `skills-pilot/工作产物/12`。
- **结论(锁定,有效性不复议)**:
  1. **"设计/实现漏洞能否 skill 优化掉" = 能** —— 靠验证脊(AH- → built-vs-spec),**非逐个 patch bug**。doc-vs-doc 门禁 + 合成 eval 抓不到这类。
  2. **它真机械核对、非橡皮章**:盲核#2 抓出我第一次修不全 = 强证据。
  3. 用例**当时就列了**(02-prd「v1 第一类=Docker web 服务」)→ 洞是**设计→impl 保真度掉(Signal #5)**;且 03-tech-solution **L133 设计阶段就自标**"auto-boot 启发式无专门 skill 覆盖"。
- **优化杠杆(direction · 最重要)**:真正该优化的**不是 patch 单 bug,是让设计 skill 可靠为新型/启发式逻辑产出完整 AH-**(库当前短板)→ 后面 093 自动守 = **Signal #5/#6 的正面解路径**。后续"skill 优化"按此方向,别再逐个补低价值 gap(09 backlog 那些)。
- **关系**:坐实 D-015/D-018(验证层价值)+ D-016(门禁找红线)+ D-021(真栈实证),把"验证脊有效"从断言变实证;与 Signal #5/#6 互锁。
- **不复议**:验证脊有效性已证。

## TD 剩余未锁项(非阻塞,Path B 期间或之后决)

- TD-02 租户(`Q-02`→单租户)/ TD-05 门禁(`Q-03`)/ TD-06 契约(`Q-05`)
- **状态**:PRD §10 有推荐默认,**未正式锁**;均不阻塞 Week 2
- **提醒未来 Claude**:这 3 项引用时标「待定」;Q-01/Q-02/TD-03 已由 D-010/D-011/D-012 锁定

---

## 决策模板(以后加新决策用)

```
## D-NNN · <短标题>
- **日期**:YYYY-MM-DD
- **决定**:<一句话>
- **理由**:<为什么>
- **影响**:<对其他事情的影响>
- **不复议 / 何时复议**:<时机>
```

---

## D-023 · skill 优化必须通用 / 项目无关(用户 06-04 二次强调)

- **日期**:2026-06-04
- **决定**:所有 skill 优化必须**通用、项目无关**。触发可以是某个具体项目的真用 bug,但**修的是底层通用类**,SKILL.md 里**零项目专有字样**。
- **理由**:用户两次强调"不要弄成只针对 RepoProbe 的 skill / 做成通用的"。skill 是给 N 个团队 × 任意项目复用的,绑死单一项目就丧失价值。
- **范例(正解)**:Windows 路径 + UTF-16 两个 RepoProbe bug → 不是"加个 Windows 路径处理",而是 `082` 加 `BK11_portability_boundary`(任意跨环境输入:路径分隔符/编码·BOM/换行/locale/OS 来源↔执行)。**grep 验证:编辑后 082 零 RepoProbe 字样**。
- **影响**:每次"真用挖洞→修 skill",先问"这 bug 属于哪个通用类",修那个类。守 D-019(优化现有)+ 本条(通用化)。

## D-024 · builder 自己 = Pilot 1 的真外部用户;停止"去找外部用户"的追问(用户 06-04 拍板)

- **日期**:2026-06-04
- **决定**:**builder 真用 RepoProbe 撞 bug、提需求,本身就是真外部用户验证**。不再把"找一个我没造的真人"当未答的 north-star 前提反复追问。
- **理由**:用户明确"我就是真外部用户"。他真用(web UI 丢 repo)暴露了 detector / 路径 / 进度 等一串我没预料的洞 —— 这正是外部用户才给得出的真实信号,且比"找别人"更直接。
- **影响**:① 停止 G2-nag(每轮结尾不再建议"去找外部用户")② 用户的真用 bug 报告 = 一等 skill 优化信号,即时通用化修复 ③ "N 个团队"仍是长期目标,但 Pilot 1 价值验证以"builder 真用"为准。
- **教训**:用户反复说"感觉没用 / 没启动起来"时,真因往往是真实可用性洞(服务 down、路径不认、无进度),**先修可用性,别转移成"需要别的用户"**。

---

## D-025 · 静态/mock 路径加 LLM「1 分钟速览」= 有限重开"解释"(用户 06-04:mock 输出没意义)

- **日期**:2026-06-04
- **决定**:RepoProbe 静态/mock 报告除原始 surface 外,加一段 **LLM(qwen)读 repo 出的『这是什么 + 技术栈/怎么跑 + 接口按功能分组 + 值得注意』1 屏速览**(= 当初 breakdown 砍掉的 F017)。无 key 优雅回退到原始清单。
- **调整(对 feasibility 的"不做解释"做有限松绑)**:原 feasibility 定「不做解释(explain = DeepWiki 红海)」。理由 = **D-024**(builder 是真用户),他两次说"路由清单没意义"——真用户要"看懂它",不是 inventory。
- **边界(不滑进红海)**:只做 **1 屏速览**(非交互 wiki、非 Q&A),且差异化仍是"**+ 能不能真跑 / 怎么跑**"(速览服务于跑验,不是独立文档产品)。
- **影响**:`llm_summarize` 进 `boot`→`report`;重 repo 跑不起来时,速览成为主要价值(替代"一坨路由")。实测 hermes-agent:qwen 正确判系统类型 + 7 组接口 + 3 条带真实模块名的架构/风险。

## D-026 · RepoProbe 范围收窄:真跑只保自包含/有约定 repo,重栈给速览+诚实诊断(用户 06-04 拍板)

- **日期**:2026-06-04
- **决定**:RepoProbe **不再追"真跑任意 repo"**。**真跑** 只对**自包含 + 有运行约定**的 repo 保证(无需外部密钥/模型权重/外部服务、端口可发布);**重栈/需外部依赖**的(ML 权重、密钥、多服务、host 网络)→ 给 **LLM 速览 + 诚实"超出真跑范围 / 需 X"诊断**,**不假装跑、不再逐边缘打补丁**。
- **收窄理由**:原 PRD"零配置自动跑验(丢任意 repo)"前提太大。用户真用(D-024)连撞 `document_recognition_system`(要 tesseract+模型权重)、`hermes-agent`(host 网络+API 默认关+要密钥)都真跑不了——这是**"自动跑任意 repo"的固有难**(E2B/Modal/Devin 同样做不到),非可补的 bug。再修 host-network/超时/端口 = 对着填不平的坑打补丁。
- **边界/真实价值**:真跑窄但真(`_sample_web` 18.9s 绿 + /health 200);速览是重栈那块的现实价值。RepoProbe 定位 = ① **Pilot 1 已达成的 skill-dogfood 夹具**(真实产出 = 打磨硬的 skills,见 D-023/025 + 一串通用修)② 一个"自包含 repo 的 boot 冒烟 + 任意 repo 的 LLM 速览"小工具,**不是通用真跑器**。
- **影响**:停止追真跑覆盖率(host-network endpoint 等不再修);web UI tagline 改诚实(说清适用范围);**投入重心回到 skills 本身**(北极星 = skills,RepoProbe 是夹具)。不算推翻 D-020(它仍是"真产品",只是范围收窄到诚实可达的)。

## D-027 · "完整功能" = 4 支柱模型,落进 025(统一 Signal #5+#6 · 用户 06-04 定义)

- **日期**:2026-06-04(session #6)
- **决定**:一个"完整功能"的判据 = **4 支柱**(用户拍板):① 原始信息来源(provenance)② 完整实现链路(触发→处理→数据副作用→结果状态)③ 完善操作过程(全 CRUD + 动作 + 各自权限/审计)④ 异常处理机制。落地 = **优化现有 `025-requirement-completeness-check`**(加 `## Complete-feature model` per-feature 核 4 支柱 + `feature_completeness` finding + `## Provenance check` + `provenance_gap`),**非新建 skill**(守 D-019)。
- **理由**:① 用户实战洞「PRD 不可能穷举后端功能」→ 中间产物需"功能→伴生需求自动推导";② 这把搁置已久的 **Signal #5(链路保真)+ Signal #6(完整性推导)统一成一个可执行判据**;③ verify 先确认 025 已有 2/3 轴(create→delete symmetry + D5 异常)→ 只补真缺口(provenance + 全 CRUD),**没重复造**。
- **支柱②归属(别混层)**:实现链路 = **spec 侧在 025**(核"链路说清没"=纵向可追溯,治 Signal #5 横向散片)/ **运行时在 093+113**(核"链路跑通没")。
- **实证**:demo 在 hub-oa auth 821 行真 PRD 上跑 4 支柱 → 揪出 **2 真 gap**(组织缺改/归档、用户缺复活),经真 Java file:line 实锤"PRD 漏、代码有"(`SysOrgServiceImpl.edit:125`/`OaReactivationController:43`)= Signal #6;TG 登录判 complete(4/4)= 不逢扫必报。产物 `skill-fork-b/hub-oa-auth-025-complete-feature-demo.md`。commit `f2438fc`。
- **不复议**:Phase 3 前(同 D-019 优化现有、不增条目)。

## D-028 · G2 首个强正信号:dream_true 团队独立核实全部确认 + 进入修复

- **日期**:2026-06-09(session #2,交接包发出后)
- **事件**:`HANDOFF-to-dream_true-team.md`(skills-pilot)发 dream_true 团队 → 团队**起 4 个子代理独立亲核** → §2 九条 + agent-reported B6/B7 共 **12 findings 全确认**(含 critical 提权标"可直接利用")。仅 **2 处文档定位修正**(非实质反驳):① 幂等中间件文件路径我 handoff 标错(`idempotency_management/api.py`〔44 行 Protocol〕→实为 `inbound/http_api_management/api.py` 的 `_idempotency_gate`;三条结论全对,**093 agent 原路径本就对、我压缩成一页时弄串**)② "record_cost 静默吞失败"过度(写库失败会抛标 FAILED 非静默;真 bug = 非原子 + 按产物文件跳过 → 崩溃窗口永久漏记,他们确认且列最高危)。团队产出**完整修复方案 + 估时 + 建议顺序**,等 builder 定范围 + §3 产品决策即开工(声明每项独立提交 + 回归测试)。
- **对 G2 判据(远强于 D-017)**:D-017(video_ai)= 6 真 1 误报、novelty 不够、混合偏正;**本次 = 真团队 + 4 代理独立验证 + 12 条全确认 + 已排期执行**。= 北极星 D-016/D-018 一路"待验真团队采纳"的**首个强正答**。
- **双向可信**:团队 2 处修正我方文档(且抓出我 handoff 把幂等路径标错)= **真核非盖章**,同 D-017 video_ai 团队反向修正我 3 处的健康闭环。
- **诚实边界**:团队已确认 + 承诺修,但 **fixes 尚未 land**。终局采纳 = fixes shipped + 团队明确"愿在 CI/上线前持续跑这套核对"(同 D-018 G2 显式价值口径)。当前 = **强正信号,非终局铁证**。
- **后续**:按团队 act 深度更新(修了几条 / 是否沉淀回归测试 / 是否继续用)→ 兑现则升"首个真采纳闭环";9 缺陷拆 dev task(N250/Path C 未在 dream_true dogfood)可顺手补。
- ✅ **兑现(2026-06-09 同日续)= D-018 完整价值模型首次在真团队真产品闭合**:团队**已 ship 修复**——**P0 提权** `9a8ef59`(is_admin 搬出开放 metadata→User 专用字段〔**采了我 §3 建议**〕+ update_user 剥离 client is_admin + PUT/DELETE 加守卫 + 专用 admin 置位端点 + 旧数据迁移;`test_privilege_escalation_blocked` 把 exploit 钉成回归测试)+ **#31 删整集级联** `2e287b9`(门禁唯一 blocker;enumerate-owned-skip-shared);**13 回归测试沉淀进 CI,后端 1808→1821,mypy/ruff/audit 零 drift**。= 发现器→人裁定→**沉淀确定性测试**(D-018 三层模型)**首次在真团队真产品跑通**;北极星核心假设("团队用 skills ship 得更稳")首个真证据。**诚实边界**:2/9(修的是无产品决策依赖的两条 = critical + 门禁 blocker);#32-#39 pending(部分卡 §3 决策);团队与 builder 有连接(非冷启动外部团队);**"把这套核对变成每次发布前常规"未证**(从"用了一次"到"采纳成习惯"是下一道坎)。团队修 #31 时**自挖出 #39**(render/配音 StorageAPI 同类删集缺口)= 深度 engage,正属今日折进 `015`/`017` 的 `cleanup_coverage` 镜头类。
- ✅✅ **完整兑现(2026-06-10)= 北极星核心假设完整证实一次**:团队把 **#32-#39 全 8 条 dev-task 包完整 ship + 推送 + 过门禁 + 回归测试进 CI**(2/9 → **9/9**),**照 baked §3 决策逐条 + 钱链顺序守住**(原子 `32a6205` → 对账 `337dad5` `update_cost_amount` 绕幂等 → 预算闸 `5bd8bc9`..`c1bcdb3`;余 #32 `c979a9d` / #35 `fe514a1` / #36 `8d80cd5` / #37 −4400 行 `1ac7494`+ / #38 `2abd754` / #39 `aa19090`)。**关键**:团队落的这个包 = 当天我反验过 `055 defect_remediation_mode` 能自动产的**同形状** → skill 现实价值(不只我手搓)坐实。**operator 亲核 #34 预算闸 4 点全 PASS**:authz `platform.py:649` fail-closed(is_admin 专用字段不可自封 + docstring 标「自抬限额属提权类」= 团队吸收 authz_input 镜头)/ 红线 `ai_jobs.py:407` gate 在入队+provider 前 raise 零副作用 / 闸读已花费依赖 #33 原子落账(我排顺序的意义)/ 边界 strict `>` 取我反验默认。**月度 reset 团队诚实降级为 all-time**(`CostRecord` 无 created_at 实锤,operator 认)+ operator 挑出 **global all-time 总闸 = 全平台终身预算 → 运营久必全平台停摆**(比单用户撞墙急)+ 3 次要近似(estimate 占位 / TOCTOU / 未装 fail-open)。= 发现器→人裁定→可执行修复任务→ship+CI **全链跑通**,修法我建议、决策我 baked、顺序我排、形状 055 反验过。**升级:「首个真采纳闭环」→「完整真采纳闭环(9/9)」**。**诚实(终局仍未到)**:团队与 builder 有连接(非冷外部)、**用了这一轮 ≠ 纳入每次发布前常规**;月度降级是真 v1 折损(global all-time 尖锐面)。另一份交接 R-DOMAIN-BLIND 架构分层团队在跑(Phase 0+B4+B1 done,余 roadmap)。verify-only:亲读 dream_true 真码核 #34,没碰其码/git。
- ✅ **续(2026-06-10)= REVIEW-budget-gate-34 复核件团队同日全采纳**:operator 核 #34 的反馈(§2 global all-time 停摆 / §4 created_at 提前 / §3.3 fail-open 静默)整理成可转发件 → 团队 commit `c0b0261` 全实现且注释直接引用「operator 复核 §2/§4/§3.3」;月窗 gate→check→report 端到端贯通(`current_month_window()` UTC 月初 → per-user/global 月度 reset,根治 §2 all-time 停摆),我独立核过 + 1825 pytest 绿。**团队正确分辨优先级**:§2/§4/§3.3 act、§3.1(estimate 校准)/§3.2(TOCTOU)by-design 跳过 = **用判断非盲从**(核对被当工程输入而非圣旨)。= 今天 G2 第三次即时兑现(#32-#39 ship / REVIEW / created_at)。verify-only 亲读核没碰 git。
- 🔭 **终局读数(2026-06-10 盯 R-DOMAIN-BLIND)= D-028 终局到一半、框架强于预期**:团队没停在修完 #32-#39,把**核对本身制度化**了——domain-blind gate(`scripts/tier_audit.py` + `test_foundation_domain_blind.py` + ADR-0018)= 架构分层核对编译成 **CI 红线 + ratchet 棘轮(只增不减、越来越严)**;ADR-0018 维护机制白纸黑字「**定期人/LLM 审计扫残差 → 能机器化的沉淀回 gate**」+「扫描器是**候选生成器**、抓 8 成、余靠周期审计补」= **团队用 D-018 发现器哲学原话写进 ADR**。**= 制度框架/文化已建(远强于「用了一轮」)**。**但缺口**:这套常规**只挂「架构分层」一维**;我的**缺陷/安全/资金发现器**(money_flow / authz_input / cleanup_coverage / 死码 / spec↔code)仍**一次性**(#32-#39 修完即止、未接进定期审计回流)。**终局最后一公里** = 把发现器镜头接进团队已有 ratchet:可机器化的(cleanup_coverage / 死码 / authz_input)仿 tier_audit 做 gate、需判断的进定期 LLM 审计清单(顺水推舟,框架已就位)。R-DOMAIN-BLIND 进度:Phase 0✅ + Phase 1 5/6✅(剩 B3 observability)+ Phase 2(DB 收口)待,用户主动⏸️;handoff #30-#39 全✅。verify-only 只读核(git + .task-plans + ADR)。✅ **demo 实证(同日)**:`cleanup_coverage` 镜头用 ~120 行 tier_audit 式纯扫描器跑通(`cleanup_coverage_gate.py`)——v1 报 3 → operator 复核真码发现 **2 分层假阳**(低层 store vs 高层 Service)→ v2 class 级收紧到 1;真码 EpisodeService covered 不误报、合成坏例当场红 = 防退化有效。= **最后一公里可行性已证**(强在防退化、抓初始需写删配对;同 domain-blind gate 模式可挂团队 ratchet)。`06-demo-cleanup-coverage-gate.md`。✅ **第二个 gate authz_input 已 demo**(`authz_input_gate.py`:权限位 × 开放 metadata、非 `.pop` 剥离 = RED;当前 289 文件 **0 误报**、反证抓到**真 P0 漏洞行** `projects.py:173`〔修复前 `metadata.get("is_admin")` 做 authz = 提权根因〕、合成退化红,**比 cleanup 更干净**)→ 现成机器化 gate 增至 **2**(覆盖 #31/#36/#39 + P0),给团队页 authz 行 🔶→✅、建议「两 gate 一起先挂」。`07-demo-authz-input-gate.md`。
- ✅✅✅ **终局机制面落地(2026-06-10 续)= 最后一公里走完**:团队 `e472aec` 把 cleanup_coverage + authz_input 两发现器镜头**接进 ratchet**——但**没照搬**我的行扫原型:先 4 子代理对抗验证(头条论断全成立)→ 挖出原型 4 真缺陷(多行签名截断假红 / 方法名注释自覆盖假绿 / 模块级误归属 / 命名耦合假阳)→ **AST 重写再挂**(`scripts/cleanup_audit.py` 270 行 + `scripts/authz_input_audit.py` 156 行 + 棘轮测试进 pytest + **ADR-0020** 两轨 + `periodic-defect-audit.md` 第三轨〔死码/money_flow/spec 漂移→定期 LLM 审计〕)= 缺陷/安全/资金发现器从一次性审计 → **持续 CI red + 定期清单,制度化**。**同日 055 前瞻反验全链闭合**:gate 验证副产物 orphan 级联缺陷(operator 核真)→ 冷 agent 用 055 `defect_remediation_mode` 产 4 任务包**封存于修复前**(`08-prospective-dogfood-orphan-cascade.md`)→ 团队独立修复 `9de38b5` **机制层 4 要素全中**(连「项目行保留可重试」理由都同)+ 文档命中 line-site 级(spec-25 L39/L123)→ 对照(`09-prospective-scoring-orphan-cascade.md`)抓出团队 2 真缺口(阻断语义未钉死 / 存量无决策记录)→ 反馈 → 团队 `8517765` **同日全采纳且 commit 正文引用「skill-strengthening 09」文档编号**(最硬一类采纳痕迹)。= 今天 G2 第四、五次即时兑现;**预测在先**的反验比 #32-#39 回顾性高一档。**出 055 新信号**:remediation_kind 判据「pre-existing 失败」需锚定发现时刻(团队标 fix vs agent 标 add_missing_control,缺失级联类总能事后构造红)→ 下轮 D-019。**诚实**:终局剩行为面(「每次发布前常规」是否成习惯,机制≠习惯);dream_true 全史 607 commits 单作者 kk_li(+Co-Authored-By Claude),按「与 builder 有连接的团队」口径不改定性但记录在案;前瞻反验同模型族非完全独立。
- **不复议**:G2 首个强正信号 + 首个真采纳闭环(事件事实)。
- ✅ **行为面首个数据点(2026-06-11)= D-028 终局另一半开始有动静**:dream_true `12eb015`(06-10 18:48,距 `e472aec` 机制落地仅 3.4h)**自发执行** `periodic-defect-audit.md` §1 wired-but-unused 镜头 → SoftwareConfig 死配置区(零生产消费者)全栈删除(契约/三实装/HTTP/前端/schema v2 双侧迁移),commit 正文引用「§1 wired-but-unused 镜头」+「经用户确认整面删除」+ 先例 #37、R11 文档先行、pytest 1884 + 前端 85 + 全门禁绿。**意义**:定期审计轨(第三轨)不是写完搁着,落地当天就被用来挖出并清掉一处真死码 = 「核对成常规」的行为面有了第一个真动作。**诚实**:这是「定期审计轨被用了一次」,**≠「每次发布前固定跑 gate」的习惯**;机制→习惯的长期判据仍看后续发布周期是否反复发生。verify-only:只 fetch + git show 亲读。
- ✅ **R-DEMAND-PULL 折信号(2026-06-11)= remediation_kind 判据歧义消解进 055**:接 06-10 前瞻反验预注册分歧①(团队 commit 标 `fix`、agent 标 `add_missing_control`,缺失级联类总能事后构造修复前必红的测试 → 「能构造红测」误判成 `fix`)。折进 055 SKILL.md remediation_kind 段一条**判据消解条款(发现时刻锚定)**:「可复现失败」= 发现当时即存在的失败(线上报错 / 既有测试变红 / 用户可见错误行为),**不含为缺陷新写断言才转红**;缺失类(缺级联 / 缺守卫 / 缺约束)归 `add_missing_control`、哪怕 commit 习惯标 `fix`;灰区拿不准标 `to_confirm`。**verify**:读回 zip 条款在、零项目字样(`orphan_items[]` 是 055 既有通用词非项目术语)、zip 完整 15 entries、**库仍 157**(D-019 改现有非新增)、334 行(+1 条款)。属「分类精度」族,**第 4 个折进 055 的同族信号**(接 06-10 #4 的 readiness/to_confirm/spike 例外/inferred)。verify-only:edit + rezip skills 库 zip(可改),留用户 commit。

## D-029 · 缺陷→修复任务能力归 Path C(055 新 mode),不归 N250/092、不新建 skill

- **日期**:2026-06-10
- **背景**:dream_true G2 win 的核心动作 = 「审计发现 → 可执行修复任务」(团队采的是**修法**:is_admin 搬出 metadata、enumerate-owned-skip-shared)。但昨天手搓 `dev-task-pack-pending.md`(457 行 9 DT)坐实:**`DT-id + fix-approach + file:line + deps + estimate + acceptance=回归测试` 这个对象,落在 N250(止于 triage/repro)与 Path C(只接 greenfield 方案)之间,整库无节点拥有**(dogfood §C)。agent 当时建议**新建** `defect-remediation-task-generation` skill。
- **决定**:按 D-019(不新建、扩现有)拨回 → 折进 **Path C 核心原子 skill `055-development-task-breakdown` 的新 mode `defect_remediation_mode`**。055 消费缺陷记录(090 分类 / 091 定级 / 092 复现,或审计 / 静态 / 事故发现)→ 产 remediation task,字段:`maps_to_defect`(多对一)/ `remediation_kind`(fix / add_missing_control / delete_dead_code / contract_align,与 task_kind 正交)/ `fix_approach`(方向非从零设计)/ `target_site`(已知 file:line + provenance)/ `priority`(继承严重度 + `priority_override_reason`)/ DoD(回归测试钉死不变量 + 假阳性 guard);+ `R11_remediation_task_grounded` 机读门禁。
- **为什么 055 不是 092**:① 092 Boundary 明文「reproduce a *failure*」,对 #34(新功能,无可复现失败)/ #37(死码删除)本就 strain(dogfood §445);让它产 fix-approach/estimate/deps 是越界(task planning 非 repro)。② 055 本职 = 产 dev task,defect→fix-task 是它的 **brownfield 输入变体**,复用 task_kind/estimate/deps,不受「failure」约束,原生覆盖 4 种 remediation_kind。③ Path C macro 无实体文件(Grep 证 `solution-to-dev-tasks` 仅在文档)= D-002 概念 path = N180 块,其产 task 核心原子 skill 即 055。
- **落地**:+26 行 6 处、库仍 **157**(D-019)、零项目字样(D-023)、readback PASS。092 不动(保持产 defect record 上游),055 主动声明消费它 = 最小侵入。log = `skill-strengthening/04-fold-log-defect-remediation.md` + `_repackage4.py` + `recon/055-SKILL.md`。
- **诚实**:R11 落 SKILL.md 正文(agent 权威面);`references/task-breakdown-self-check.yaml` 仍 R01-R10(reference 辅助,本批不动 references,同昨天三圈 fold 处理)。
- ✅ **已反验通过(2026-06-10 同日)**:冷上下文 agent 只读强化后 055 + HANDOFF(严格禁读 phase3 手搓版,tool_uses=3)、用 `defect_remediation_mode` 重产 12 task(`phase3/055-cold-reproduce-dt-pack.md`)→ operator 对照手搓 `dev-task-pack`(DT-01..08):**remediation_kind 4 型全对**(#34=add_missing_control / #37=delete_dead_code / #38a=contract_align / cost·锁·渲染=fix)、DoD 范式对(delete 用「不可达+套件绿」不塞回归测试)、priority override 独立复现手搓 DT-07 结论、provenance 诚实(inferred_site / agent_reported)+ 正确应用 HANDOFF 幂等 file:line 勘误、R01-R11 全 pass;**2 处比手搓更优**(幂等按 kind 拆 fix+add_missing_control;B7 用 spike 先判删/补)。反事实证据=agent 指认「没 delete_dead_code『不可达+套件绿』那句会给死码塞回归测试」。**边界**:同模型非完全独立;prompt 喂的「机制待定→to_confirm 不 blocked」恰是 055 一个真空(见下信号①)。
- ✅ **反验又出 4 个 055 新信号**(下一轮 D-019,元洞察「连验证都在出信号」):① to_confirm vs blocked 中间态(产品决策齐+机制待定→provisional 不 blocked)无判据 ② to_confirm 无 schema(question/why/blocks_code/decide_by)③ spike 承接 × R11 冲突(修复形状待判定用 T7_spike,DoD 走 spike 范式非 R11 回归范式)④ 缺陷无源头 P 级时优先级无指引。连同 089 `audit_intake` / 091 `latent_risk` 进下轮。
- **同轮 D-019 剩余**(用户本轮只点第 3 条):① 089 `audit_intake` 入口(审计缺陷无失败测试 / 无 signature)② 091 `latent_risk`/`priority_override_reason`(潜伏缺陷低估)。
- ✅ **续(2026-06-10)= 6 同族信号已折**:反验 4 个(to_confirm-vs-blocked 判据 / to_confirm schema / spike×R11 例外 / 无源头 P 级 → 055)+ dogfood 2 个(089 `audit_intake` / 091 `latent_risk`)全折进现有 3 skill,**库仍 157**(D-019)、通用(D-023)、verify-first、PASS;`05-fold-log-6-signals.md`。6 个同属「不确定/待定诚实标注精度」族 = D-018 发现器→人裁定贯到字段级。
- **不复议**:能力归属(Path C 拥有 defect-remediation;N250 止于 triage/repro 的边界清晰)。

## D-030 · skill 优化 = 需求驱动,不是库存驱动(「优化全部 157」是反模式)

- **日期**:2026-06-10(用户问「怎么设计流程长久优化全部 skills」→ 5-agent workflow 调查 git/引擎/eval 实测后定调)
- **背景实测**(workflow,非估):**真内容强化只 19/157 = 12%**;94/157 连 validator-sweep 都没碰(发布 N270-290 全 11、文档 N330-360 全 18 整簇 0 真改);全库演进压缩在 7 天(06-04~06-10)= 冲刺非巡航;改动**绝对 demand-pull**(19 个真强化每个追到一次具体真用事件)。
- **决定**:**不追求「优化全部」**。skill 沿真实使用需求被打磨,**覆盖率是 forward-use 的副产物、不是 KPI**。一个 day-1 状态、从没被真项目跑过的发布/文档 skill,被优化 0 次**恰恰是健康的**(无需求信号去指导方向,凭空改=猜=项目反复警告的「磨刀替代证刀」「刀磨利≠有人用」,已亲手叫停过一次=Signal #7 连撞 4 阶段)。
- **长久流程 = 已在跑的 6 引擎管线固化 + 一个缺环**:S0 改账本(STATUS 的「库仍 157」机械复述 → 需求驱动 coverage-ledger:真改/day1/latent-gap)· S1 信号捕获(forward-use 主引擎,当天折回,fold 循环)· S2 cold-agent 防循环把关 · **S3 = 缺陷检测 eval(唯一该新建、最高杠杆)** · S4 机器化沉淀进 ratchet · S5 盲区只事件驱动扩张(不主动 sweep)。
- **S3 缺陷 eval(待用户拍是否建)**:现 eval 4 维饱和 0.90 + gt_similarity 混 D-012 模型偏差 = 分不出强弱 skill。ground truth 已就位(~24 条已验证缺陷 + 2 个跑过的 gate 是现成「检测器跑真码+判定」实例)→ 走**机械判据(命中 file:line)规避 D-012**,输出「哪个 skill 该优化」排序。是项目自标「唯一没建成的轨」(06-08 #6 提过未做)。
- **跑几年的 3 颗雷(须主动防)**:① **D-019「只增不减库恒 157」= ADR-0018 自我腐烂定时炸弹**(SKILL.md 膨胀、字段互咬如 spike×R11;棘轮只增没删机制)② SKILL.md vs references/*.yaml 漂移(R11 在正文、yaml 停 R01-R10)③ 记忆系统自身先腐烂(STATUS 单条几千字、CLAUDE.md 155 stale)。
- **N scaling**:N=1 该做的是把 dream_true 推成「纳入每次发布前常规」(D-028 终局)非优化更多;**N=10 时 D-019「只增不减」必须松绑**,主动作从「优化」变「治理」(删/合/仲裁/回归门)。
- **不复议**:需求驱动框架(由 12% 实测 + demand-pull 形态 + 与 D-019/north-star 一致 决定)。S3 建不建 = 用户拍。
- ✅ **S3 已建(2026-06-10,用户「建」)**:`_eval/defects/defect_eval.py`+README——6 通用缺陷 fixture/3 类(authz/cleanup/contract_drift=2 gate 判定逻辑+1)、机械臂无需 key、**机械判据(命中行号)规避 D-012**、clean 负样本测 FP;跑通=全 recall=1.00/FP=0.00+scorer 自检三态分明;llm 臂(注入 SKILL.md+delta)接口就绪需 endpoint。**自印证 D-030**:138 个 day-1 skill 没 fixture 可建(没东西练过)=S3 把盲区从「不知道好不好」变「可见地不可测」,measurement 跟真用走不跟库存。

## D-031 · OA 日检测循环 = dogfood/S3 扩源/回归盯防,不是 G2(用户=carrier 时观测的是自己)

- **日期**:2026-06-10(用户提「检测 OA→给文档→我提交→每天复扫合并代码」+「现实项目不会一步步来」+「给团队东西不一定进 commit」)
- **背景**:OA(hub-oa)反馈断路——给团队东西不一定进 commit。用户提的循环把 carrier 换成自己(用户自己提交)→ 反馈进用户 commit、git 可见,解了断路的一条边。3-agent workflow(reverify+对抗压测+设计)评估。
- **关键实测(reverify)**:master-audit 12 条 confirmed **逐条对当前 `origin/master@0da96ef0` 实读 = 12/12 still_holds**(含 H5 首度 operator 确认);团队「修复」commit `379c61d0`/`8ea01d42` **不在 release 线 master**(在 dev_xy/master_bak)、即便合入也没碰发现 loci → **审计零 stale**,第一份文档现成。
- **决定:循环值得建,但定位钉死 = dogfood + S3 第二域(Java)扩源 + 回归盯防,NOT G2**。压测核心:循环里**没有一个 OA 团队的决策进入回路**(发现/提交/复检全是用户自己)→ 它把 G2 要观测的「团队对发现的反应」剪出回路;**用户每默默修一个,团队就少一次体验闭环 = G2 被主动消耗**,非推迟。= Signal #7「磨刀替代证刀」最新变体(刀真在切菜但没人买刀)。
- **收紧后的循环(无状态/事件驱动,治「现实不一步步来」)**:① watermark(master SHA)有新合并才扫、否则闭嘴(非日历)② 只扫 master 合并 diff、dev_* 只读不报 ③ findings 台账(指纹 rule+file+symbol 无行号)日报只报 NEW/FIXED/REGRESSED ④ 每条进文档前对 HEAD 重核+盖 verified-at SHA 戳 ⑤ **机械确定类(死码/死端点)直接提、语义类(authz/资金/双签)必先过 OA dev/release owner 点头**(那个 owner-pass = G2 入口,防 proxy-commit 断 D-018 人裁定链)⑥ 每条沉淀确定性回归 ⑦ 蒸馏成 Java fixture 喂 S3 + 团队 bugfix 抽检镜头缺口。日循环只跑 2 个机械 gate(0-FP);横切镜头需 judgment、只事件驱动上(团队动热区/发布前)。
- **G2 升级判据(落在对方 git/流程,不落你的扫描日志)**:①发现过 owner 裁定再 commit ②非用户作者 commit 引用发现 ID ③团队主动索要下轮 ④团队把 gate 接进自己 CI/checklist。四条任一出现前,产出一律记 dogfood。
- **真 G2 动作仍是社交动作**(日循环替代不了):master-audit 12 条 + pre-ship 门禁 + 2 detector-gate 打包送 OA release owner,趁他们正改双签时机最佳。
- **不复议**:OA 循环定位(dogfood/S3,非 G2);reverify 12/12 still_holds(事件事实)。

## D-032 · full-audit 四道闸方法经 OA 团队 triage 验证 = 确认层近零假阳、不认可层 = 团队认同我的下沉判断

- **日期**:2026-06-15(session-3)
- **事件**:OA 团队对全量审计模块 02/03(31 条)逐条 triage:新提 9 个正式禅道工单(#2970-#2978 带严重度)、已存在复用 5(#2947/#2948/#2949已修/#2954/#2955/#2957)、跨模块归他人 5、不认可 12。
- **关键数据**:**12 条不认可 100% 落在我自己已分的「潜伏 / 核实正常 / 对抗推翻 / 诚实降级」非确认层,无一条是我确信判的 bug**。我的「确认问题」层(HIGH/MID-HIGH operator 真基线亲核)近乎全被采纳为新提或已存在工单。
- **四道闸各自被独立验证**:① **基线完整性门救场**——quickLoginEnabled 我用 git show 真基线把 high 纠成 low-mid 潜伏、明指 L55 有服务端守卫,团队拒理由正是 L55 守卫(否则按旧工作树误报会递个 high 假阳给团队)② **对抗复核门**——4 条 workflow 误报(三方同步签 / 清退不清 TOTP / 双 L6 三主体 / 内部 HMAC)团队拒 = 我 workflow 对抗层早已推翻的 N1/N2/N3/N6 ③ **活码 vs 僵尸门**——僵尸/配置门控项(doLoginByForB/C、callback_query、TgSigner、Widget devMode)团队拒「不可达 / 无活攻击面」④ **诚实降级**——jwt_blocklist 我标「非无状态 JWT 危机、sa-token uuid 会话等价」,团队拒理由一字不差。
- **结论(指北极星)**:38% 不认可不是方法失败,是方法**诚实分层**在起作用——把没把握的下沉标清楚,团队拒就是认同;确认层真实 FP 率 ≈ 0。**= full-audit(PRD-first + 四门 + workflow 对抗 + operator 真基线亲核)产出 triage-clean 交付件的首个团队级证据**,强于 cold-read(5 发现→4 bug),这是 2 模块→9 新 bug 入库带定级。
- **诚实边界**:测试已确认入库 ≠ 研发已 fix(看后续引用 #2970-#2978 的 fix commit);仍是 N=1 内 detection 侧 G2(团队消费我审计),非团队用 skills 建产品。
- **对 D-031 全量审计的影响**:方法成熟度证据 +1,但 17 铺开仍守每模块 operator 真基线亲核——本轮正是亲核 + 基线门挡住假阳才换来零假阳确认层;**确认「先亲核再交、四门必走」对,不放宽**。

## D-033 · 「四道门」verify-before-claim 预检 + reality-finding 6 字段格式 折进 093(D-030 demand-pull 又一次兑现)

- **日期**:2026-06-16(session-1)
- **决定**:把 OA 全量审计(模块 01-04)反复用出的「PRD-first 审计四道硬门」+ 团队钦定的 6 字段 finding 格式,折进 `093-quality-gate-check`(N260),作为 reality-check finding 的**发出纪律**。优化现有、**库仍 157**(D-019)、**通用零项目字样**(D-023)。
- **折入内容**:
  - ① **四道门 = verify-before-claim 预检纪律**(独立 H2 段,与既有四轴 built_vs_spec/reverse_coverage/cross_service_contract/money_flow_completeness **正交**——四轴找候选,四道门判候选能否作为 confirmed 发出):Gate1 canonical-first(下「需求未定义/未规定」前先读权威 spec)/ Gate2 跨名反查+端到端可达(交叉引用 §reverse_coverage+§cross_service_contract,加对称陷阱:over-claim missing 与 over-correct implemented 两向都假阳)/ Gate3 活码 vs 僵尸(交叉引用 cross_service 第4型 wired_but_unused + 070 死 guard,加「未证在线前不评质量、不信为真实现」)/ Gate4 基线完整性(把 cross_service 的 release-ref 提醒泛化成横切所有 reality 断言)。任一门未过 → 降级 provisional/unknown/deviation 交人裁。
  - ② **6 字段格式** = symptom/code_evidence/spec_basis/impact/regression_test/source,**fix-direction 故意省略**(合红线:只报现象证据、修法 owning team 定);code_evidence/spec_basis 精确定位;regression_test = D-018 distill 在 per-finding 粒度;与 blocker_registry.resolution_path 写明分工(它是已确认 blocker 的清障追踪,不是代码修法)防矛盾。
  - ③ **R10_reality_finding_contract** 契约规则:confirmed reality finding 必带 6 字段 + 过适用四门,否则降级(降级非 reject,与「发现器非 per-PR 硬门禁」+ evidence_confidence 对齐)。
- **理由**:四门在 OA 模块 01-04 审计**反复用出**且团队 triage **反向验证有效**(D-032:12 条不认可 100% 落在四门下沉的非确认层);6 字段是团队钦定格式、已落官方缺陷管线(#2991-#2997)。= **D-030 demand-pull**(真用→暴露/验证方法→折进库),非库存驱动。
- **验证**:ultracode workflow(map→design→3 对抗复核 lens〔generic/duplication/coherence 全过〕→synth,8 agents/460k tokens)设计+对抗验证,operator 落地+逐项亲验——baseline 在原 zip 实跑确认 >350 行 strict warning **既有非本次回归**;改后 384 行,validator 非 strict 0 error exit 0、strict 仅那条既有 line-count warning(零新 error);grep 全文零项目字样;rezip round-trip entry list 与原 zip 23 条完全一致;**库 157**。
- **诚实边界**:`scripts/test_skill.py --strict` 因 SKILL.md >350 行**改前(354)就红、改后(384)仍红**=既有失败、非本次回归、非阻断(非 strict CI 绿);四门折入**未真 dogfood 反验**(下次拿真模块当 ground truth,看新一轮审计是否正确触发四门 + 按 6 字段产出)。
- **不复议**:折入有效性 + 归属(reality-finding 发出纪律归 093);四门措辞可按真用继续优化(同 D-019/D-023)。
- ✅ **dogfood 反验有效(2026-06-16 同日,模块 05 I1_bonus)**:把四门 + 6 字段在真模块 05 跑(workflow wgsu7rs1g,75 agents/5.3M tokens,基线 c2c11c8f,每 agent 显式跑四门)+ operator 亲核四条最重 → 确认 24 + 潜伏 1 + 待产品 1 + 推翻/正常 4。**四门 demonstrably 起效**:最硬证据 F-I1-020——初判「I2→I1 主流程整体未实现」的 S2 红线,Gate2 跨名反查发现异名 live+单测通道(OaBonusPlanController.publish→publishWithDualL6→createOrSubmit + I2_PUBLISH_INBOUND 审计,operator git show 实证)整条假阳推翻;另 3 条(F-I1-006/007/R1-02)经 Gate2/3 降为正常,多条 over-severity 经 Gate2 降级,F-I1-014 经 Gate3 判潜伏,R1-01 经 Gate1+TODO 判待产品;6 字段输出全干净;无一门误杀真缺陷。**Gate4 又对我自己救场**:工作树落后 origin/master 329 commits,审计全钉 c2c11c8f。= 从「机制入库」升「dogfood 反验有效」。**诚实**:四门只过滤「缺陷在基线是否真存在」,排不了运行时业务影响优先级(FX 红线单币种被掩盖、F1 僵尸连锁需集成测试);本轮无 operator 抓出过度断言(03/04 各抓到过,本轮零)。落 `D:/projects/skills-pilot/oa-pilot/full-audit/05-bonus.md`。

---

## 已被推翻 / 修正的决策

## D-004-OVERRIDE · Pilot 1 不再"造 Skills Studio 工具",改为"用 agent 跑真实 SDLC"

- **覆盖日期**:2026-06-01(session #3)
- **新决定**:Pilot 1 = 选一个**真实产品**,用 **agent(Claude Code,团队都在用)直接调用 skills**,跑完整 **产品 → 研发 → 测试 → 部署 → 反馈** 全流程。**不再造任何 wrapper 工具 / 不配 apikey / 不写"怎么用"文档。**
- **推翻理由**:
  - builder + 同事本来就用 agent;**agent 就是 skill 的 runtime**,Skills Studio(Web UI + key 配置 + 使用说明)是多余的一层
  - "感觉没用"的真因 = 给 agent 用户造了个他们不需要的壳,还喂玩具输入
  - 真正的验证 = 用 skills **真 ship 一个产品**(= 北极星本身),不是点一个 UI
  - 这一步同时收编前两个纠结:**它就是价值验证**(A/G2),**也是 skill 优化信号**(真用暴露弱 skill,比合成 eval 真)
- **教训**:别为"让 skills 可用"造工具 —— **先问"用户怎么工作"**。他们用 agent → skill 直接进 agent(SKILL.md 可分发/安装),不需要 UI。Skills Studio 是一个 session 的弯路(但证明了 skills 真能出好工件,artifacts 留作 dogfood 样本);代码留作参考,不再投入。
- **影响**:接下来按 SDLC 5 步推进一个真实产品;第一步 = 定产品方向 + 写 PRD(Path A,在 agent 里跑)。Skills Studio 服务可关。

**修正决策格式**:
```
## D-NNN-OVERRIDE · <原决策标题>
- **覆盖日期**:YYYY-MM-DD
- **新决定**:<>
- **推翻理由**:<什么数据 / 什么事件让我们改主意>
- **教训**:<下次怎么避免同类错判>
```


## D-034 — 三条系统性缺陷类折进 051/052 的 N170 设计硬规则(D-030 demand-pull 又一次兑现,从方法侧扩到设计侧)

- **日期**:2026-06-17(session-2)
- **背景**:OA 全量审计 01-18 反复撞见、且被团队 triage 反向验证有效的跨模块系统性缺陷,折成通用设计硬规则进 N170 现有 skill(verify-first 确认是真 gap 再加;通用零项目字样 D-023;库仍 157 D-019)。
- **决策**:
  - **051-audit-trail-design 加 R08_audit_write_durability(reject)**:审计写的持久性必须相对业务提交定义——emitted-event ≠ durable-record;审计写与业务提交解耦(异步/独立事务/best-effort)时必须有丢失检测 + 对账或重放,禁止业务已提交而审计可静默丢失且无检测。与 R02 append-only(防改写已写入记录)正交。来源=审计 #13 平台审计异步旁路非同事务=04/06/12/14/16 审计缺口总根(并在 06-17 薪酬回归分析里再确认该异步架构)。
  - **052-authorization-model-design 加 R08_grant_ceiling_enforced(reject)**:授予/改派/角色变更点必须强制授予上限不变式(授出权限集合 ⊆ 授予方自身可授出集合);端点 can-call 鉴权门 ≠ what-can-be-granted 上限,两者都必须有。与 R02 SoD 正交。来源=审计 #14 提权 S1(无角色层级校验,低层级可授高层级)。
  - **052 加 R09_lifecycle_full_revocation(reject)**:主体终止/暂停态转换必须枚举并原子吊销全部能力面(次要/代理角色、已委托授予、长期令牌/会话、二次验证登记、渠道访问等);部分吊销留终止主体仍可操作。与 R03 delegation TTL 正交。来源=审计 #07 清退不清令牌 / #12 冻结员工仍可考勤。
  - 每条同步落进四处镜像(v2-contract Hard gate rules 表 + checklist + SKILL.md inline rule_results yaml + common-failure-modes F11/F12)+ Required-output-schema 字段 + CHANGELOG;rule_results 区间 051→R01-R08、052→R01-R09。
- **方法**:ultracode workflow(run wf_b3089341-6c1,13 agents)草拟 + 每条 3 镜头对抗验证(通用零项目字样 / 非重复 R01-R07 / 设计 altitude + 抓准类);altitude 镜头把规则从机制枚举改成属性锚定(051 耦合模式列举非穷尽;052 授予上限泛化成 ⊆ 自身可授出集合,避免误拒 capability 模型)。operator 精确字符串替换 apply + 写新 zip 验证(frontmatter utf-8 复刻校验 + inline yaml safe_load + 零项目字样 grep + namelist 18 原序保留)后替换原文件;quick_validate.py 的 exit1 是其 Windows gbk 读 UTF-8 的既有 bug(对原始未改 skill 同样崩),非本次问题,已用 utf-8 复刻验证替代。
- **影响**:demand-pull 从「审计方法折进 093」(D-033)扩到「审计发现的缺陷类折进设计侧 051/052」=库的设计闸现在能在设计期挡掉这三类最严重的系统性缺陷;真团队 triage 是反向验证(#13/#14/#07/#12 都被独立确认)。**✅ 续(06-17 session-2,用户「需要」)= detection 侧两模式也折完**:054 加 R08_control_enforcement_verified(缓解 critical/high 威胁的控制必须核实真生效、占位桩按 missing 计入 residual risk,把 F2 从建议升硬规则)+ 070 扩 dead_guard 检测目录 3 形态(stub_control 触发却空转 / no_producer 有读无写僵尸 / unreachable_state 再入态零入边卡死)+ 3 rule_kind 进 catalog。**5 个系统性模式全折完**,跨 4 skill(051/052/054 设计侧 4 规则 + 070 检测侧 3 形态),库仍 157、通用零项目字样(banned 计数不增法验)。诚实:折入未真 dogfood 反验(下次拿真设计任务看 R08/R09 是否正确触发);改动仅在 skills 库(可写区),零碰他人仓。


## D-035 — 折进库的 5 条规则经第二项目(dream_true)跨域 dogfood 坐实通用 + 收 5 条 round-3 精化信号

- **日期**:2026-06-17(session-1)
- **背景**:D-034 把 OA 审计(Java·HR/财务)反复撞见的系统性缺陷折成 051/052/054/070 的通用规则。需验证这泛化是真通用还是贴 OA。拿 dream_true(Python·AI 视频·完全异域)做第二项目审计 + 跨域 dogfood(用户「用这套验证下 dream_true」)。
- **决策/结论**:
  - **规则跨域通用坐实(D-023 验证)**:审 dream_true 5 域@58f9158,折叠规则在异域真找出 PRD 自承的结构缺口,零结构性误报于反例。dogfood_verdict 5 fired_correctly / 5 na(正确判不适用)/ 5 false_positive(多为误归因非凭空报)。**070 系迁移性最强**:no_producer 命中 update_cost_amount 对账回填僵尸(三后端+协议全实现、生产零调用方,operator 亲核坐实)、unreachable_state 命中 WorkflowStatus.PAUSED 等零入边死枚举(operator 亲核全仓零限定使用);051_R08 钉资金落账持久性(spent 恒 0 不回填、script 二次扣费窗口)且监控≠审计边界正确克制;052/054 正确判不适用未强行命中。
  - **收 5 条 round-3 精化信号(下次折/调措辞)**:① 070_unreachable_state 靶严格限「零入边非终态」,显式排除「入边存在但过窄/仅人工触发」(DEAD_LETTER)与「未接线的文档承诺分支」(style anchor 指向不存在字段)——本次 3 条误报全源于把这两类塞进零入边靶;② 070_no_producer 补「只定位结构 gap、其业务量级影响另判、勿在规则结论量化成本/损失」——build_resume_plan 被 ADR-0015 产物跳过稀释成本,规则 over-claim;③ **052_R08 需锋利区分 (a) 授予上限放大『授出 ⊄ 授予方自身集』(真靶) vs (b) 资源端点缺属主校验致 can-call 门过宽/IDOR**——dream_true AI job 越权(任意用户 cancel/delete 他人 job)是 (b) 被误配到 (a);**要么收窄 052_R08 只管授予上限,要么新增一条「resource owner enforcement」规则承接 (b)= 设计决策,待用户拍**;④ 052_R09 加范围门「仅当终止吊销是已 committed 需求才判缺陷;PRD 明示该协作/多主体能力本期不实现则判 rule_not_applicable 并降底座残留,不当确诊」;⑤ 051_R08 触发逻辑不改,固化排除提示「监控/可观测(best-effort trace、fire-and-forget 告警)非审计落账面、丢点可 by-design、判前先 Gate1 核 PRD 是否把该写持久性相对业务提交定义」。
- **影响**:① demand-pull 的强证据再加一层——规则不止从 OA 折进来,还在第二个异域真项目找出真问题=真通用(D-023);② full-audit 方法在第二项目第二语言成立(map+verify+operator 亲核);③ dream_true 得 12 条观察件(`D:/projects/skills-pilot/dream_true-prd/AUDIT-2026-06-17-observations.md`);④ round-3 精化是 dogfood 自产的下一轮 demand-pull,其中 052_R08 split 是真设计决策待拍。**✅ 续(用户「1 2」)= round-3 五精化已应用 + 052_R08 走向已决**:051 R08 监控≠审计排除固化 / 052 R08 收窄只管授予量级 / 052 R09 范围门 / **052 新增 R10_resource_owner_enforcement(IDOR/BOLA,收窄 R08 误吸的资源属主校验,入现有 052 库仍 157)** / 070 unreachable_state 排除窄入边+空承诺、no_producer 去量化。apply 验证过(R01-R10 连续、banned 计数挡下 CHANGELOG 误写的项目名)、库仍 157。dream_true 观察件转团队版 HANDOFF-audit-2026-06-17(路径相对其仓根)。诚实:round-3 未再 dogfood 反验;observation 待用户转团队。verify-only:dream_true 全程只读、零碰 git;写只在 skills-pilot + skills 库。


## D-036 — 北极星正解=「单兵 × skill 干出一个团队的产出」,team-adoption 不是目标(用户 2026-06-17 纠正)

- **日期**:2026-06-17(session-1)
- **背景**:本 session 我反复把北极星误框成「必须有一个外部团队采纳/跑这套 skill 才算数」,据此把今天一整天的 solo 工作(一个人审 OA 18 模块/折 5 类规则/跨域验证库通用)自贬成「detection 舒适区、没推北极星」。用户纠正:「目标就是一个人解决一个团队的任务。什么都要团队来跑,意义不是太大了。」
- **决策(北极星正解)**:
  - 北极星 = **杠杆**:一个 1-3 人单兵单元,用这套 skill 干出过去要一个团队才能干的活(从想法 ship 到生产)。CLAUDE.md「N 个小团队 × 1-3 人」本就是这个意思——单位是单兵/微团队,N 只是规模。
  - **team-adoption / 别的团队来跑,不是目标、也不是前提**。它顶多是「产出够不够真/够不够团队级」的一个【验证信号】(G2 证明我找的 bug 是真的、设计是可落地的);但「必须有团队采纳才算数」是错的 bar。而且追求别人采纳/marketplace 本就是 CLAUDE.md 明列的 anti-goal。
  - 判断一个动作推不推北极星,标准是:**它有没有让「一个人 + skill」产出了「团队级」的成果、把任务真的解决?** 不是「有没有团队来跑」。
- **影响**:
  - 重判今天 = **强北极星**:我一个人用 skill 做了团队级的活(审一整个项目 18 模块、强化库、跨域验证库通用)。之前「舒适区/没推北极星」的自评是错的,基于错的 bar。
  - 重判 Path B 跑 OA 模块:对的事,但尺子是「这份技术方案够不够团队级——一个人能不能据它 ship、不需要一个设计团队」,不是「OA 会不会采纳」。
  - G2/team triage 仍有用(验证产出是真的),但降级为「验证信号」非「北极星本身」。记忆 [[north-star-solo-leverage]] + [[oa-live-n2-candidate]]/[[dream-true-g2-closed-loop]] 的「team adoption」措辞按此理解。


## D-037 — skill 系统的价值机制:PRD 必然不完整,流程是下游「问题最小化器」(用户 2026-06-17,D-036 的兑现机制)

- **日期**:2026-06-17(session-1)
- **背景**:用户经几轮把愿景钉成机制:「实际开发 PRD 不可能面面俱到全描述;需要后续通过 skills 将问题尽量减小化。」配 Path B forward dogfood 实据(skill 链正向把团队 PRD 漏掉的 IDOR/提权/审计三横切洞逼进设计)+ operator 核团队代码(6b3c4e31):团队对这些洞是开发各自隐式拍脑袋填——IDOR 填成 org 数据范围(够用)、#14 同类填成裸奔提权 S1(崩)。
- **决策(机制正解)**:
  - PRD 结构性不完整是【常态、不是缺陷】,别追完美 PRD。它是业务需求文档,系统性漏横切/非功能约束(IDOR/审计耦合/授予上限/并发/幂等…),因为那些是"所有模块通用、大家都懂"的隐性约束。
  - skill 流程 = 下游【问题最小化器】(尽量减小化,非消灭),三阶段补:设计期注入(N170 051/052/054/049/050)→ 静态拦截(N210 070/072/073/074)→ 测试验证(N260 095-099);硬规则触发【不依赖 PRD 写没写】。
  - 两类分治:① 非功能/横切漏洞 → 规则驱动【系统性注入】,随规则集完整度趋近零;② 业务逻辑歧义(PRD 无法预先拍)→ 早期【显式化为决策点】最小化成本(决策一次、不让 N 个开发各自猜→防走偏/不一致/返工/沟通),决策本身仍归人/产品。
  - 引擎 = 棘轮:detection(审计找横切类)→ fold(折成硬规则)→ prevention(流程正向自动注入);每折一条,流程对该类永久覆盖、对所有未来 PRD 生效。
- **影响**:
  - 这是 D-036(solo 杠杆)的兑现机制;benchmark(skill vs 团队)尺子 = 残余问题最小化程度,不是零缺陷。
  - 后续折规则优先级 = 把横切漏洞类的规则集补全(缺口:限流/熔断/超时、错误码契约一致性等仍未成硬规则)。
  - 本 session 一整天 = 在转这台棘轮(7 条新规则 + Path B 正向证生效)。记忆 [[north-star-solo-leverage]] 已补此机制。


## D-038 — B3 调岗做成第一个完整三层 benchmark(skill 生成 vs 团队生成,defect-prevention 计分)= D-036/D-037 的首个完整实据

- **日期**:2026-06-22(week-of-06-22 计划执行)
- **背景**:detection 侧(OA 01-18 审完)是舒适区,北极星增长前沿=正向生成三层 benchmark。之前只做完设计层一层(B3-transfer-tech-solution)。本周按 `D:/projects/skills-pilot/oa-pilot/benchmark-b3/PLAN-week-of-2026-06-22.md` 把 B3 补齐到 PRD/设计/代码三层全对照、全计分。
- **做了什么**:Gate4 钉基线(hub-oa 4379d56d 工作树落后 408 全程 git show / hub-oa-prd 3e423f9)。Layer1 Path A workflow(6 agents 零限流)从团队需求工程工作区(非成稿 PRD)盲重生成 B3 PRD + 4 设计硬规则族(025/051/052/054)通用应用 35 finding;operator 逐条核团队成稿 canonical PRD。Layer2 复用 Path B + 在 real master 重基线三洞。Layer3 对 3 横切控制点 targeted 生成实现/契约 + 同库对抗 verify,operator 比团队真码 @4379d56d。产物全落 `…/benchmark-b3/{A-prd-skill-vs-team.md, B-design-rebaselined.md, C-code-skill-vs-team.md, B3-three-layer-scorecard.md}` + `_pathA-*/_layer3-*`。
- **校准结论(future session 别重论)**:
  - skill 的 defect-prevention **最强在需求/设计层 = 把团队流程结构性盲掉的横切约束逼成显式问题点**;**代码生成是方向对、需硬化的草图**(同库对抗 verify 抓出 CP1 TOCTOU/403-404 泄露、CP2 resolver 留空可恒放行、CP3 旧切面未拆=draft 非成品,但 skill 链内部 discover→verify 闭环跑通)。
  - **三层收敛是最硬证据**:grant-ceiling(052R08,同 #14)+ 审计耦合(051R08,同 #13)两个核心增量在需求层(团队 PRD grep 零命中 / §4.5.3 同事务 vs §4.5.6 Kafka 异步矛盾)、设计层(skill 逼出闸/耦合分类)、代码层(executeApprovedTransfer:961 无等级闸 / 平台审计 @Order(100) post-commit + DLQ)三处独立可见互相印证=同一洞从需求漏到代码=D-037 实证。
  - **诚实分层**:① skill 输入是设计感知的需求工作区非纯业务白纸,论点是「给同样输入能否逼出团队盲掉的横切」非「凭空重导设计」;② 「需求缺显式声明」≠「系统有可利用漏洞」(grant-ceiling/实例属主是真代码缺口,审计耦合团队 DLQ 部分兜住);③ benchmark 算残余问题最小化程度(D-037)非零缺陷;④ 三层都对团队已覆盖处如实记功不贪功(052R09/原子事务/工号唯一/撤回本人/DLQ+重放=团队已有)。
- **意义**:**第一个完整三层 datapoint**,比横向多铺设计层更硬;是 D-036(单兵×skill≈团队产出)经 D-037(流程是下游问题最小化器)机制的首个完整实据。引擎=detection→fold→prevention 棘轮:051/052/054 这批横切规则从 OA 审计 detection 折进库、本次在 generation 三层正向兑现。
- **下一步选项(待用户定,非本决策锁死)**:① 扩第二模块做三层(验证非 B3 特例)② 代码层从草图推到「生成+团队既有测试跑过」一档 ③ 补横切规则集前沿缺口(限流/熔断/超时、错误码契约一致性)折进库。
- **不复议**:B3 三层 benchmark 已完成(事件事实)+ 校准结论(skill 强在设计期显式化横切、代码生成是 draft)。记忆 [[north-star-solo-leverage]]。
- ✅ **续(2026-06-22,用户「1 2 3」三个下一步全做,顺序 3→2→1)**:
  - **#3 前沿横切规则折进库(库仍 157)**:053 加 `R08_resilience_stance_on_boundary_deps`(warn 级 R06 特化,跨边界 at_risk 依赖 mitigation 须就超时/重试(含刻意不重试)/级联保护/资源隔离四面各表立场 + by-design 豁免)+ 045 加 `R09_published_code_contract_stability`(reject,active 码语义/HTTP 相对上一 contract_fingerprint 无静默漂移,跨协议 transport waiver 豁免)。**对抗 verify 主价值是防膨胀**:两条草稿都被发现与现有内容重叠(053 resilience 已被 B07/R06 覆盖、045 碰撞已被 F3 覆盖+跨层一致是 044 的 altitude),收窄到真正正交残值(053=立场完整性、045=版本稳定)才折入。= discover→verify 闭环防 ADR-0018 自腐(D-030 反库存驱动)。通用零项目字样、namelist 保持、R01-R08/R01-R09 连续。诚实:两规则未真 dogfood(留下次),后被 #1 的 N1 部分兑现(见下)。
  - **#2 代码层从草图到「硬化+真跑过」**:CP2 grant-ceiling 纯逻辑核硬化成独立可编译 Java + 回归/硬化测试,javac+java 10 passed/0 failed/exit 0(Java 21)。直接堵对抗 verify 的洞:resolver 返 Optional(空=fail-closed DENY 堵恒放行)、signerEid 空不放行不 NPE、退化封套构造期拒。`…/benchmark-b3/_layer3-hardened/`。证明 scorecard 里「代码生成是 draft、需硬化」的 draft 经一轮硬化纯逻辑核可达真跑过;集成仍需团队 build。
  - **#1 第二模块 N1 费用报销验证 B3 非特例 = 泛化成立**:N1(money-flow+链上+审批)横切画像与 B3(authz/生命周期)鲜明不同。Layer 1 Path A(同规则集换 025/050/051/052/053)盲生成压出 **050 幂等 + 053 韧性为主面(各 5 missing),052 grant-ceiling 弱化成 implicit**(B3 恰相反)= 同一规则集随模块画像自适应触发。Layer 2 operator 亲核团队真码收敛:skill 050 R02 盲逼出的「资金写须 DB UNIQUE 双层」正是 `assertInvoiceNotDuplicated:1135` SELECT-only race 残洞;链上支付是 Phase-1 stub(未来需求,Gate3 判);withdraw 有属主门(团队覆盖)。**#3 刚折的 053 R08 在 N1 外部依赖(G1 汇率/链上 RPC/对象存储/TG Bot/UBO API)正确 fire = 新规则首次 dogfood 验证有效**。`…/benchmark-n1/N1-benchmark-summary.md`。诚实:N1 做 Layer1 全+Layer2 全+Layer3 聚焦一靶点(发票去重双层),非完整三横切点;泛化核心问题 Layer 1+2 已答。
  - **合并意义**:D-038 从「一个模块三层」扩到「两个画像迥异模块都成立 + 棘轮规则集补前沿 + 代码层 draft 可硬化到真跑过」。北极星(D-036 单兵×skill 团队级产出)证据 +1,机制(D-037 流程是下游问题最小化器)在第二画像兑现。
- ✅ **续2(2026-06-22,用户第二/三/四轮「1 2 3」)= 三迥异画像泛化 + 折入规则两道关全过 + 第三个控制硬化**:
  - **前沿规则共折 3 条且全经对抗 verify 把关**:053 R08 韧性立场(warn 级 R06 特化)/ 045 R09 错误码版本稳定(reject)/ 048 R06 值快照一致性(warn 默认+reject 矛盾态+结构化豁免)。对抗 verify 2 条判冗余收窄(053/045)、1 条判真新颖(048 R06);**dogfood 9 盲判 9/9 fire 全对、048 R06 三分支全判对**(验 altitude 修法不 cry-wolf);045 R09 软边(waiver→NA)已微调。库恒 157。
  - **代码层 draft→硬化到真跑过 = 3 个控制**:CP2 grant-ceiling(authz,10/10)、发票去重(money-flow 并发,11/11)、FxLockResolver(值快照,8/8),javac+java 全绿。draft-needs-hardening 在 authz/money-flow-并发/值快照三类一致;同库对抗 verify 每次抓出真实现 bug(恒放行 resolver / finally-删锁-早于-commit / amount 漂移+一致性自校缺)。
  - **三迥异画像泛化(最强)**:B3 调岗(authz)主面 052 grant-ceiling、N1 费用报销(money-flow)主面 050 幂等+053 韧性、K1 考勤(并发-控制)主面 049 并发+054 控制强制。**同一套规则集三次自适应压出模块对应横切主面,每次 skill 盲发现↔operator 亲核团队真码收敛**(grant-ceiling↔无闸 / 发票R02↔SELECT-only race / **geo↔GeoVerifyServiceImpl 恒 PASS stub**)。D-034 折入的 054 R08 首次在真模块(K1 geo)命中 present-but-inert 安全控制。= 规则集自适应不是某画像特例,泛化在三画像立住。诚实:N1/K1 是 Layer1 全+Layer2 全(+N1 Layer3 三横切点),非 B3 那样全三层;geo/停登录是团队有意 Phase-1 分期非确诊。

---

## D-039 — 验证靠读当前代码(不靠 commit);并反查「团队改了但我没发现的」= skill 漏检盲区(用户 2026-06-23 拍板)

- **日期**:2026-06-23
- **纠正背景**:此前 G2 watch 一直靠「commit 引禅道# + 在途/并 master」追团队是否处置我的发现。用户纠正:研发可能自己发现就顺手改了、不提单不引号,盯 commit 会漏掉「静默修复」。
- **决定(方法论,适用所有外部团队不止 OA)**:
  1. **验证靠读码,不靠 commit**:对我检测出的**每一个**发现,去当前代码(对准目标 ref、不信工作树)读、看问题实际改了没(已修/未修/部分),给代码证据。不以 commit / 禅道# 为准——有些 bug 研发自己发现就顺手改了、从不引我的号。
  2. **闭环 = 发现 → 读码验证是否解决 → 优化 skill**(不是发现就完)。
  3. **反向维度(最有价值)**:扫团队代码的修改,找**团队改了、但我当初没检测出来**的安全/质量问题 →那是 skill 的**漏检盲区**;团队修了说明是真问题、我没发现说明 skill 该补 → 据此优化 skill 补盲区。
  4. **目的**:skill 越补越完善 → 单兵用 skills 产出越强(北极星 D-036)。这把 G2 从「看团队有没有 commit 引我的号」升级成「看代码实际状态 + 反向学团队修了什么我没抓到」。
- **守红线(不变)**:验证/反查全程只读(git show/Read 对准 ref、不碰 git 状态);产出是观察(现象+代码证据),不替团队下结论、不代提工单(红线三)。「漏检盲区」是对**我方 skill** 的批评、不是对团队代码的裁定。
- **关系**:深化 D-018(发现器→裁定→沉淀)+ D-030(demand-pull skill 优化),把优化输入从「我发现的」扩到「团队修了我没发现的」。更新记忆 [[oa-live-n2-candidate]] 的 G2 盯法。
- **不复议**:验证方式(读码非 commit)+ 反向学盲区维度已立。


## D-040 — D-039 第二域(报销)跑通 = 库在「单点缺陷」已成熟,真盲区收敛成「跨站点一致性」家族(demand-pull 指向新前沿)

- **日期**:2026-06-24
- **事件**:D-039 验证循环推广到第二业务域=报销(workflow wf_f43da20a,34 agents/1.9M tok;基线 85902c6e→当前 master 03a891375,团队报销模块 1480 行重写 / 14 新文件)。读码验证我方 full-audit 01-expense 的 11 发现:**9 FIXED + 2 PARTIAL + 1 UNFIXED**,均当前码行级支撑(非 commit message)。反查盲区 25 候选 → 对抗 verify(默认怀疑+亲核归因+核现有规则覆盖)收成 **15 真盲区 / 10 否决**。
- **两个校准结论(future session 别重论)**:
  1. **库在「单点缺陷」类已成熟**:10 条否决多为已被现有规则覆盖(052 R10 资源属主/R11 default-deny、049 lock_decision_tree/S04/S05、050 R02 双层、051 R02/R08),或归因错(我方原始已点中换皮)。= 单点安全/质量缺陷库基本封口,继续在那挖边际递减。
  2. **真盲区全收敛成一个家族 =「跨站点一致性不变量」**(单点检测物理查不出、须跨站点核全局不变量):聚合一致(当前记录已入聚合又被叠加=重复计入)、多实现一致(同规则两实现谓词方向相反、单边修复致分叉)、跨工件边界一致(同阈值散在应用码/部署脚本/工作流引擎且开闭不一)、单位一致(带单位量未归一化即比固定标量、工作流引擎条件站点常被只看主代码的审计遗漏)、事务边界一致(多表写无事务/事务内非事务副作用回滚不对称/审计写跨入口事务不对称)、枚举语义一致(枚举成员字面量复制漂移、语义重载后排除型过滤误吞)。
- **折库方向(最高杠杆,待执行 + 带 dogfood 反验)**:070 承接 6 条(enum_member_literal_drift / aggregate_double_count / divergent_duplicate_logic / divergent_duplicated_boundary / unbounded_keyspace_no_ttl / 状态值语义重载回扫)= 主;048×2(跨工件/跨表单一事实源)/ 049×2(非原子限流 check-then-act + SELECT-then-update TOCTOU)/ 050(事务内非事务副作用回滚对称)/ 051(审计写跨入口事务对称,R08 细化)/ 032(带单位量归一化)/ 053(工作流引擎条件站点单位混比)/ 054(失败姿态矩阵,R08 横向扩)。
- **诚实边界**:① 15 条均 generic+归因+防膨胀三关过,但**尚未真 dogfood 反验**——synth 自点名是「应补方向」非「已验证规则」;折库闭环 = 灌规则进 070/048/049/050/051/032/053/054 → 重跑同一 OA diff → 验新规则机械命中本批现象且不误伤 9 条已 FIXED ② 是否构成缺陷/严重度/立项由 OA 团队判,盲区是对我方 skill 的批评非对团队裁定;现象成立由 OA 测试按回归点确认;不代提工单 ③ 单域单项目信号,跨站点一致性是否真通用还需第三域或第二项目(如 dream_true)再验(同 D-035 跨域坐实纪律)。
- **关系**:坐实 D-039(读码验证+反查盲区维度在第二域成立)+ D-030(demand-pull)+ D-037(棘轮 detection→fold→prevention)。把库的下一前沿从「补单点横切规则」明确为「补跨站点一致性/全局不变量检测」。文档 `D:/projects/skills-pilot/oa-pilot/verify-loop-expense-2026-06-24.md`。记忆 [[north-star-solo-leverage]]。
- **不复议**:验证结果(9 FIXED 等)+ 「单点已成熟 / 真盲区=跨站点一致性家族」校准。折库具体规则文本与是否全折,留执行时按对抗 verify 逐条定(防膨胀)。
- ✅ **续(2026-06-24,用户选「2」先验跨域再折)= 第三域(薪酬)坐实 D-040「跨站点一致性家族跨域通用」**:薪酬域 workflow wf_60930f0c(44 agents/2.66M tok;基线 85902c6e→master 03a891375,团队薪酬模块 132 文件/7933 行重写)。
  - **读码验证 16 发现:4 FIXED / 9 UNFIXED / 3 PARTIAL**,全当前码行级支撑。**读码非 commit 兑现最强一次**:F8 四闸专属码/F4 哈希链虽 #2993/#2996 曾被 revert 仍以当前码判(已重新在位=FIXED);**F3-D14 不止 UNFIXED 还更糟**——闸口翻 PAY_EXECUTED 还落一条 PAYROLL_PAID 审计而 OA_PAY_ORDER 永停 PENDING=账面背离+审计谎报已付;F2 工资明细 UNFIXED(DB 仍可改,新哈希链是 batch 级非 per-record,单行原地改+批次合计不变检不出)。
  - **反查盲区:33 候选 → 20 真盲区 / 13 否决**。13 否决多为已被 049/050/051/052/054 现有规则覆盖,或换皮(C2/C7 我方原始已列),或前提被亲核证伪=防膨胀正常工作。
  - **D-040 坐实(强证据,非部分)**:cross-site-consistency **16/20=80% 主导**,与报销域(15 条)同为头号家族;**三个子型在两域同形复现**(divergent_duplicated_boundary 同概念多站点实现强度/审计不对称、同语义错误码协议状态分叉、同结构跨工件无单一权威源)=「家族跨域通用」最硬证据;同时薪酬独有 4 新子型(派生键双向一致性、control_basis_literal_drift、authoritative_inert_divergence、特权旁路跨等价路径不对称)→ **通用框架 + 域增量,二者不冲突**。
  - **折库最高杠杆=070**(20 盲区命中 10 条):composite finding_kinds = divergent_duplicated_boundary / authoritative_inert_divergence / rogue_producer / control_basis_literal_drift / dominated_guard_unreachable / exclusion_guard_swallows_terminal_state;次=045(5 条,错误码族协议状态一致性 R10)/ 048(3,跨工件/派生键单一事实源)/ 049(3,链尾 TOCTOU+状态翻转原子)/ 052(2,break-glass 跨等价旁路对称)/ 054(3,present-but-inert 状态域 guard+代理边界覆盖)。
  - **诚实**:两轮 synth 都自点名【未真 dogfood 反验】——折库闭环须用本批 35 盲区(报销 15+薪酬 20)作 ground truth 重跑升级版 070/045/048/049/052/054,验机械命中且不误伤已 FIXED 项。文档 `D:/projects/skills-pilot/oa-pilot/verify-loop-payroll-2026-06-24.md`(30KB)。
  - **下一步明确**:D-040 既坐实跨域通用,**折「两域共现子型」进库(最高置信:070 divergent_duplicated_boundary + 045 错误码族一致 + 048 跨工件单一源)= 棘轮 prevention 步**,带对抗 verify 防膨胀 + dogfood 反验;域特定单子型留复现再折(纪律:折跨域已证的、留单域待证的)。
- ✅ **续2(2026-06-24,用户选「4」)= 三 fold 全 apply 进库 + 首次带 dogfood 反验闭环**(workflow wf_b40b385b,28 agents/1.18M tok)。三阶段:draft+防膨胀 → **dogfood 反验**(把草拟规则机械套到真 OA 代码,正例核 recall、FIXED 项核 precision)→ synth go/no-go。结果 **3 GO**:
  - **070 加 finding_kind: divergent_duplicated_boundary**(跨 ≥2 实现点的控制发散:谓词极性相反/强制强度不一/姊妹站点锁不对称/冗余双判致死分支/等价旁路审计不对称五形态)。dogfood **recall 5/5、precision 0/5 误伤**;防膨胀核过与 magic_number(单点)/dead_guard/stub_control/registration_fail_open(单控制失效)均正交。落点 SKILL.md finding_kind bullet + v2-schema-catalog 枚举。
  - **045 加 R10_error_code_family_status_consistency(warn)**:语义同族错误码须映射一致协议状态+命名,码名随控制基数迁移,声明场景=实抛场景。dogfood **recall 4/4、precision 0/3**;与 R02(单码完整)/R09(单码版本冻结)正交。落点 SKILL inline + 解释 bullet + checklist + common-failure F8 + CHANGELOG v4.1.0。
  - **048 加 R08_cross_artifact_single_source_of_truth(reject)**:同值/schema/派生键复制进 ≥2 不同类型工件须单一权威源。dogfood **recall 2/4(synth 正确判另 2 是错配正例:PAY-critic#4 属 032、PAY-critic#1 是 stale baseline,非规则弱)、precision 0/3**;synth **拒绝** dogfood 提议的扩宽(会让 048 侵入 032 acceptance-mapping 轴破坏正交)。落点 SKILL inline + common-failure F11 + checklist E2 + CHANGELOG v4.1.0。
  - **operator apply 纪律**:精确 old→new 串替换(每处 assert count==1)、python zipfile 纯内存编辑保 namelist/压缩、库恒 **157**、frontmatter 不动、inline YAML safe_load 过;**genericize 修正**=045 F8 草稿混入 OA 具名码(D5_DATA_NOT_COLLECTED/NODE5_NOT_TRIPLE_SIGNER 等)→ 改占位符(GATE_A_*/`*_NOT_TRIPLE_SIGNER`),generic 扫描 \\bOA\\b+项目名全 0(守 D-023);脚本+备份 `D:/projects/skills-pilot/oa-pilot/_apply-054-070/`(apply_folds.py + fold-decision-2026-06-24.json)。
  - **意义(还了欠账)**:这是**首次「折库带 dogfood 反验」闭环**——之前 054/052/051 折入都自承「未 dogfood」,本次三条都先在真 OA 代码上验了 recall+precision 才 apply。棘轮 detection→fold→prevention 在「跨站点一致性」这一前沿类上跑通一整圈:OA 两域审计发现 → 反查盲区 → 跨域坐实 → 折库 + dogfood。**诚实**:dogfood 是「规则机械套到已知盲区代码看是否触发」,非「在 _eval 框架重审全模块」;真正的端到端 dogfood(让升级版 skill 重审一遍模块看能否自动捕获)仍可后补,但本次 precision(零误伤 FIXED)已是实质防膨胀验证。
  - **诚实边界(留账)**:域特定单子型未折(payroll 独有 4 个、expense 若干)——按「折跨域已证、留单域待证」纪律待复现;045 的 R09 当初折入时也无 CHANGELOG 条目(pre-existing,未补)。


## D-041 — 真端到端 dogfood(held-out 奖金域)裁定:折入规则 precision 跨域泛化、但 recall 严重不足 = 「判得准、找得太少」;折规则必须带可操作搜索启发式,不能只给定义

- **日期**:2026-06-24(用户选「真端到端 dogfood」)
- **事件**:对 06-24 折入的 3 条新规则(070 divergent_duplicated_boundary / 045 R10 / 048 R08)做首次真端到端 dogfood(workflow wf_06bff095,32 agents/1.7M tok)。held-out 域=**奖金 bonus**(2846 行团队重写,且明确不在 3 规则的起草样本里——排除「规则记得自己见过的实例」泄漏)。双臂设计:treatment 臂只拿 3 规则盲找、control 臂深推理穷举真值;treatment 每条命中亲核 ref 03a891375 代码裁真伪(precision),control 每条标是否在规则范围+是否被 treatment 逮到(recall)。
- **核心数据**:
  - **precision = 100%(16/16)**:treatment 盲找 16 条全部亲核属实、零误报。最硬几条全核实(approval-unlock#4 financeReview `selectByIdForUpdate` vs 姊妹写点裸 `selectById` 无锁=lost-update;package-confirm#1 双 L6 守卫 I1 双查 vs I2 缺 op1 空值守卫;approval-unlock#3 同「包不存在」一处抛 409 一处抛 404;package-confirm#3 签字备注校验挪用「作废原因」码)。
  - **recall(in-scope)= 8%(2/25)**:control 深推理找 30 条、25 条落在 3 新规则范围内,treatment 只独立逮 2 条;漏抓几乎全 classification=missed-by-rule-formulation(规则范围纸面覆盖、但措辞没把审计员导到那条具体站点)。
- **裁定(平台级原则,future 别重论)**:
  1. **precision 跨域泛化成立** = 3 规则不靠「起草记忆」、纯凭措辞就能在陌生域盲找出真实例且裁定准 → 折入的规则是「真规则」非「拟合记忆」。这一半是好消息,坐实折库有效。
  2. **recall 严重不足 = 折规则的通病**:规则措辞「定义了什么是缺陷」却「没告诉审计员怎么去找」。treatment 逮到的几乎都是注释自承「与 X 同口径/同义」显式自供的;纯结构同构(无注释提示)基本漏。**070-divergent 最弱**(in-scope 漏抓最大来源——「≥2 实现点发散无权威源」太抽象,不知去哪些站点对照);**045-R10 最强**(错误码集中单一 ErrorCode.java、码/状态/命名三轴可枚举,导引力天然高);048-R08 居中(跨工件类型差异逮得到、纯 Java 多副本常量漏得多)。
  3. **改法 = 折规则必须配「可操作搜索启发式 / 扫描锚」,不能只给定义**。例:070 应补「对同一概念枚举所有 service/impl 同名私有方法/常量逐对比强度」「结构同构整行 RMW 写点核对锁/版本字段是否一致」「注释出现『与 X 同口径/同义』即触发对照 X」——把「识别发散」从依赖审计灵感降为可机械执行;048 应明列「同一 private static final 业务阈值在 ≥2 Java 类各自定义」为强信号;045-R10 无需改。**这条适用于所有已折与将折规则**(054/052/051/070/045/048 都可能 precision 高 recall 低,值得回头补搜索启发式)。
- **副产出(满足 D-040「折跨域已证」)**:payroll 独有 4 子型在奖金域的复现核查 → **control_basis_literal_drift 复现**(驳回理由 30→20 下调,ErrorCode 留 @deprecated + 5 处 MIN_*_REASON_LEN=20 副本各持字面)、**authoritative_inert_divergence 复现**(BonusPackageSignerRole 权威枚举存在却被 controller @RequireRoleCode / param @Pattern 各自另写成员集)→ **两子型跨域已证 = 折入候选**;privilege-bypass 部分复现(倾向可折、建议再取一域)、derived-key 未复现(仍单域待证)。另有 4 条新盲区候选(out-of-scope)作下一轮 demand-pull 种子。
- **方法论收获**:**dogfood(treatment/control 双臂 held-out)本身成为平台一个验证工具**——它在零额外人工下抓出「我的折库 precision 高但 recall 低」这个我自己想不到的弱点。= D-018 发现器→裁定→沉淀在「skill 库自身质量」上的自指应用。
- **诚实边界**:单 held-out 域;treatment/control 都是有噪声的 LLM 审计(control 真值集可能漏/多,recall 8% 含此不确定);所有 OA 条目是现象+代码证据观察件、非缺陷裁定,严重度/立项由团队判、现象由测试确认。文档 `D:/projects/skills-pilot/oa-pilot/dogfood-e2e-bonus-2026-06-24.md`。
- **不复议**:「折规则 precision 易达、recall 需可操作搜索启发式」+「dogfood 双臂 held-out 是有效的库质量验证法」已立。记忆 [[north-star-solo-leverage]]。
- **✅续(2026-06-25 apply)**:D-041 prescription 落地 —— 070 `divergent_duplicated_boundary` 加 5 条可 grep 搜索锚(①注释自供锚『与 X 同口径/同义/一致』召回最高优先 ②同名符号锚 ③结构同构 RMW 锚 ④权威源成员锚 ⑤阈值字面量锚)+ 形态 (f) authoritative_inert_divergence;048 `R08` 放宽到 ≥2 同类型多副本(同一 private static final 阈值在 ≥2 Java 类)+ control_basis_literal_drift 形态 + 扫描锚(CHANGELOG v4.2.0)。**设计裁定**:两条跨域已证 payroll 子型(control_basis_literal_drift / authoritative_inert_divergence)折成『带搜索锚的形态』而非新 finding_kind —— 因 D-041 已证 recall 洞在『怎么找』非『定义什么』,只加裸定义会再造低 recall 规则。校验全过(070/048 namelist 不变、frontmatter 不动、所有 YAML safe_load、generic 零 banned、库恒 157),脚本 `D:/projects/skills-pilot/oa-pilot/_apply-recall-fix/apply_recall_fix.py` + 备份。**待验(未还的诚实欠账)**:recall 是否真从 8% 升——须拿同一 held-out 奖金域用更新后规则**重 dogfood**(workflow,待发);折后若仍 recall 低则措辞还需再迭代。
- **✅续2(2026-06-25 受控 A/B re-dogfood,wf_ee664662 / 22 agents)**:D-041 prescription **证实有效**。同一 held-out 奖金域、同一 42 条独立真值集,只换规则文本:**recall old(抽象)19% → new(锚)26%,+3 条净增;precision 两臂均 100%、零 cry-wolf**(锚不掉精度)。承重锚=④权威源成员锚(+3,最强)、⑤阈值字面量锚(+1)、③RMW 结构同构(+1);①注释自供/②同名符号本轮作确认工具非首逮(净 0)。**诚实**:老臂 19% ≠ 原轮 8%(分母 42 vs 25 不同),干净信号是受控同分母 old→new;两臂绝对 recall 都远低 ceiling = 覆盖广度洞 + 措辞洞双因。**dogfood 自指吐下一轮 3 个措辞靶**:(1)045-R10 加同族错误码 HTTP 状态一致性子锚(直击 G-02)(2)070 form b 守卫不对称扩成显式清单 lock/frozen/blank/missing-record/exemption(直击 G-07/13/19)(3)④锚补反向「权威族在位但站点用裸字面量不声明常量」(直击 G-03/05/29);估同 5 区可再净增 3~4。文档 `D:/projects/skills-pilot/oa-pilot/redogfood-ab-bonus-2026-06-25.md`。棘轮「折→验」首次带受控对比跑通整圈。
- **✅续3(2026-06-25 fold3 + 隔离式 v2 re-dogfood,wf_9c09791b / 16 agents)**:迭代闭环第 2 轮。折 3 措辞靶(045-R10 HTTP 状态扫描锚 / 070 ⑥守卫种类清单锚 / 070 ④裸字面量旁路)→ 隔离式 A/B(同 42 G、两臂都拿全 3 规则、唯一差异=折前 vs 折后):**recall before 38%(16/42)→ after 48%(20/42),净 +4 distinct gid 干净归因 3 靶;precision 100%、零 cry-wolf**。3 靶兑现 5/7(G-07/G-13/G-05/G-29 净新增、G-02 两臂都逮;漏 G-03/G-19)。诚实:本轮 before 带全 3 规则故 ≠ 原 v1 口径,唯一干净是 after−before delta;单域 n=1、after 多条行号偏(file:symbol 准)。又吐下一轮 2 靶(④补 inline event_type 旁路常量族 / ⑥加同守卫空输入放行强度对比,与 ④ 区分)。**裁定:棘轮 detection→fold→verify 连证两轮自我改进、零 cry-wolf;但下一最高杠杆=跨域泛化(锚在非奖金 held-out 域是否同样抬 recall),不是再榨奖金域 2 个 gid(n=1 过拟合风险)**。脚本+备份 `D:/projects/skills-pilot/oa-pilot/_apply-fold3/`,文档 redogfood-ab-bonus-2026-06-25.md 第七节。
- **✅续4(2026-06-25 跨域泛化验,wf_841c674a / 限流加固版)——修正 ✅续2/✅续3 的乐观**:把 bonus 上起草的全锚搬到全新 held-out 域 performance(绩效,不在任何起草样本),同 A/B 结构、3 完整覆盖区(review-flow/score-engine/role-promotion)、25 in-scope 真值。**结果:recall old 32% → new 32% = +0pp**(对照 bonus +7pp),方向与量级双双不复现;perf 上 new vs old 是命中置换(得 G11/13/14/21、丢 G02/05/09/15)非累加;precision 双臂 100%、零 cry-wolf。**裁定:锚的 recall 增益不干净外推 = 部分过拟合 bonus。** 诚实校正(不读过头):④权威源/⑥守卫清单/①注释自供三锚跨域仍各净增 1~2=真实小幅迁移;GT ceiling 压低 new(new 在 25 真值外抓了真实 RMW/僵尸码缺陷,分子吃不到);⑤阈值/R10 状态锚跨域太噪;n=2 域、±1~2 噪声。**处置:保留全锚(两域零 cry-wolf、不伤),但把『通用抬 recall』主张降级为『域内有效、跨域部分迁移、未证通用』;跨域高迁移子集=④/⑥/①。** 后续(非今日):GT 扩容含 RMW/僵尸码重测 ceiling、取第 3 域 n=2→n=3。方法论第三次抓出库自己的过度乐观(recall 洞→限流伪产物→非泛化)=D-018/D-041 诚实纪律。文档第八节。
- **✅续5(2026-06-25 多域根因调查,wf_7afda2a4 / 19 agents)——修正 ✅续4「不泛化」的过早结论(用户指示:不理想要挖为什么 + 多测几个场景)**:再测审批/生命周期两新域 + 横看四域根因。**四域 lift:bonus +7pp、approval +26pp(最大)、lifecycle +12pp、perf +0pp —— 3/4 域明显抬 recall,只 perf 例外。** ✅续4 只凭 perf 一域判「部分过拟合 bonus」是以偏概全;实情是**提示泛化得不错**。**根因(头号):提示的边际价值取决于域里有没有『被多处硬编码裸字面量旁路的权威枚举/集中阈值多副本/结构同构姊妹写路径守卫不对称』这种结构——有则提示精确指路抬 recall(approval/lifecycle 这种结构密、bonus 也有),无则空转(perf 结构稀疏,提示命中宽却落 GT 外)。能不能传 = 域的『缺陷可被锚点指认的结构密度』,不由提示本身通用性决定。** 提示迁移图:④权威源成员锚=universal(四域全产净增,主力);⑤阈值/⑥守卫/②同名/045状态=partial(各需对应结构);③RMW=抓真缺陷但 GT 没收(ceiling 吞掉);①注释自供=OA 注释文化特有(保持同步/PAT-006/Bug#),换团队不灵。**两个真问题:① 提示①/②贴域命名/注释、需改写成域无关骨架(先列权威清单+阈值清单,再反查旁路/多副本/守卫不对称;①②降级为可选辅助);② GT ceiling 掩盖真值(③ RMW/僵尸码抓的真 bug 不在真值集、不算分,perf +0pp 部分是天花板假阴)。** 处置:(1)按域无关两步法重写提示;(2)GT 扩容含 RMW 锁/死代码重测;(3)新域先做结构密度体检,稀疏域(perf)改 few-shot 不硬套通用提示。诚实:仍单仓 OA、LLM 判、±几条噪声、GT ceiling。文档第九节。**教训:单一新域的负面结论不可外推——用户坚持多测场景才纠出 ✅续4 的以偏概全,这是 D-039『验证靠多点不靠单点』在 skill 评测上的应用。**

- **✅续6(2026-06-26 提示去 OA 味 + 受控复验,design wf_3cadc60c / verify wf_7c339636)——落地 ✅续5 处置①(把贴团队习惯的锚改成域无关骨架)**:
  - **改了什么**:070 `divergent_duplicated_boundary` 检测法从「①注释自供锚=召回最高优先扫」重构成**域无关两步骨架**——Step1 机械建 权威源/阈值/写点 三张清单 → Step2 对每张反查发散(2-A 权威源成员锚=跨域主力,含裸字面量旁路 + 无源兜底,必跑满;2-B 阈值副本,048 R08 互参;2-C 守卫种类清单 + RMW 锁一致)。①注释自供 / ②同名符号**降级为「若代码库有此约定则加用、无则跳过」的可选辅助锚**;②措辞从 OA 命名前缀泛化;加 recall 不变量桥句(辅助锚指向的姊妹站点已被 Step1 写点清单 + Step2 反查独立覆盖、降级不丢 recall);同步修 form(b) 悬挂引用「见检测法⑥」→「见 2-C」。设计=workflow 3 稿 + 对抗合成 + 2 审计;审计抓出合成稿把内部代号 D-041/四域/universal 误嵌进 SKILL 正文(违 D-023 通用红线)→ operator 修后零项目字样。校验全过(23 entries / frontmatter / yaml safe_load / banned 扫描 NONE / 库恒 157),备份 `D:/projects/skills-pilot/oa-pilot/_apply-recall-fix2/`。
  - **受控复验(wf_7c339636,7 agents/698K tok)**:held-out=bonus_i1 两区(approval-unlock + package-confirm),自建 10 条真值 G,OLD 070 文本 vs NEW 070 文本同区盲找、逐条回 ref `03a891375` 亲核。**recall OLD 2/10(20%)→ NEW 3/10(30%),净升;precision 双臂 100%、cry-wolf 0**。verdict 机械判 `regression` 仅因严格 per-gid 规则:NEW **置换**了一个命中点——漏 T-PC-02(package-confirm 取包 selectById vs 姊妹 selectByIdForUpdate 锁不对称)但新逮 T-AU-02(J1 哈希链不对称)+ T-PC-01(状态守卫缺失)两条 OLD 漏的;**非净漏、净 recall 实升**(judge 自陈,且含 n=1 单采样 ±1 gid 噪声)。
  - **真残留(复验自指吐的下一靶,已折)**:NEW 把「锁不对称」锚只在一个区命中、没跨两区扫满 = 降辅助锚后跨区逐写点覆盖变稀。**已补 2-C「务必扫满」句**(同一实体写点常分散多区,须每个写点跨所有位置核到底、不得某处命中即停)——add-only 纯加覆盖、recall-safe、零删,校验全过、库恒 157。**未对此 add 做全量重验**(纯加覆盖指令结构上不减 recall;n=1 噪声下重跑多为重排,边际低)。
  - **再证 GT ceiling(✅续5 处置② / Task B 仍欠)**:两臂各报约 5 条真缺陷落在 10 条 G 之外(理由阈值 20 跨 5 副本 / APPROVE-REJECT 裸字面量 / 角色集无单一源等),名义 recall 20-30% 偏低主因是火力落在 G 未收录的副本·枚举源类。**真实 recall 被 GT 压低 → Task B(GT 扩容含 RMW 锁/裸字面量/枚举源类重测真天花板)是下一个真测量,未做。**
  - **裁定**:✅续5 处置① 落地完成,070 主路径现已域无关(= 北极星「换团队也能用」的可移植性);OA 域内 recall 不净退、precision 不掉、零 cry-wolf。诚实:单仓 OA、LLM 判、n=1、GT ceiling 未拆。apply 记录 `D:/projects/skills-pilot/oa-pilot/_apply-recall-fix2/APPLY-NOTE.md`。

- **✅续7(2026-06-26 Task B:扩容标准答案重测真天花板,wf_a69505de / 13 agents / 1.48M tok)——修正 ✅续5/✅续6 的「GT ceiling 压低真值」假设**:
  - **背景**:✅续5/✅续6 推断低 recall(20-30%)主因是标准答案太小(规则真抓到的缺陷不在真值集、不算分)。Task B 直接测:多镜头(权威源旁路/裸字面量·锁守卫不对称·谓词审计死码 3 类 × 2 区)穷举重建 bonus_i1 两区标准答案 → 逐条亲核去重成 **G+ = 27 条**(原 10 条的 2.7 倍),再用 OLD/NEW 070 在同一 G+ 上重测。
  - **结果(推翻假设)**:**OLD 在扩容后 G+ 下 recall = 7/27 = 25.9%,仍落上轮 20-30% 同带——扩容没把 recall 抬上去**。⇒ **低 recall 不是小真值集天花板压低的,是规则本身有整类覆盖洞**:predicate-audit-dead 类近乎零覆盖(OLD 0/8、NEW 1/8)。NEW = 10/27 = 37%,比 OLD 高约 11pp(真实增益,集中在 auth 5 vs 3 + predicate +1);**precision 双臂 100%、cry-wolf 0(更大更公平分母下 NEW 优势复现、零误报)**。by_class:auth-bypass-literal 12(OLD 3/NEW 5)、lock-guard-asymmetry 7(4/4)、predicate-audit-dead 8(0/1)。
  - **真天花板 ≈ 37%,被两类系统盲区压住(下一轮折库主靶)**:① predicate-audit-dead:特权自动签短路只写本地 log 不写 J1 哈希链(审计可区分性不等 form c/e)、AUTO vs FORCE 守卫发散(forceLock 私有前置旁路集中 assertCanTransit)、wflow 短路与真双签不可区分;② authoritative-bypass-literal 批:权威源(SequenceTypeEnum/AuditEventType/角色码/决策动词)在位却被 controller 注解白名单/入参正则/service 私有常量裸字面量旁路,NEW 只逮 5/12。
  - **诚实边界**:(1)predicate-audit-dead 的 8 条里数条(isAnyRejected 僵尸谓词 / StatusGuard 僵尸守卫 / 不可达态)其实是 070 **别的 finding_kind**(dead_guard/unconsumed_control/no_producer/unreachable_state)、不属 divergent;两臂被限定只找 divergent,故这部分 0/8 含**口径外扣分**——真正的 divergent 漏抓是 G-AU-09 审计不等 / G-PC-13 守卫发散 / G-PC-14 不可区分 / G-PC-09·11 锁不对称 / G-AU-05 + auth 批。(2)单域 n=1、LLM 判真值与 finding 都有噪、G+ 仍可能漏、归并口径 ±1-2。(3)两臂 G+ 外另各约 5 条真现象(mustGet 错误码不对称/EID resolver 三副本等)按只读铁律只是观察件非结论。
  - **裁定**:✅续6 的「复验三证 GT ceiling 压低真值」**部分纠回**——ceiling 确让 perf+0 类有假阴,但 bonus 两区 recall 低主因是**规则覆盖洞(整类没覆盖)而非天花板**;扩容证实 **NEW>OLD 是真改进(37% vs 26%、零 cry-wolf)**,但绝对 recall 下一步**不是再补现有形态的搜索锚、是补 predicate-audit-dead 审计不等/守卫发散形态 + auth-bypass 反查**。方法论第四次抓出库自己的过度乐观(D-018/D-041 诚实纪律)。全量 G+ 与逐条 → `D:/projects/skills-pilot/oa-pilot/_apply-recall-fix2/TASKB-gplus-remeasure-2026-06-26.md`。

- **✅续8(2026-06-26 折两盲区锚 + 折前/折后复验,design wf_53b60a54 / verify wf_ef4c5e0b)——✅续7 吐的下一靶折库,recall 几乎翻倍**:
  - **折了什么**(3 处插入 070 divergent,全泛化零项目字样、refine 不新增 finding_kind):① **2-A 加「五类旁路站点清单」**——对每个权威源逐类全扫(权限/路由注解参数白名单 / 入参校验注解正则取值集 / 各服务语义命名私有常量 / 内联 equals·switch·三元裸字面量 / DTO·前端镜像常量),不凭印象只扫一两类;② **form (e) 加「等价路径核法」**——逐目标态枚举所有到达路径,逐路径对账(审计链:某路径只写普通日志/不写合规审计链 = 审计可区分性不等;区分字段:某路径置成与强路径相同状态却不留区分标记致下游不可区分);③ **2-C 加「集中守卫旁路核法」**——若有集中状态机/前置校验入口,把「集中入口调用点集合」与「清单(3)全部写点集合」做差集,差集里用私有内联前置取代集中断言的写点 = 守卫发散归 (b)/(c)。设计=workflow 2 稿 + 对抗合成 + 2 审计(**双审计均 clean**,零项目字样/locator 真实唯一)。校验全过(23 entries/frontmatter/yaml/banned NONE 含 RequireRoleCode·assertCanTransit·J1 全 0/库 157)。
  - **折前/折后复验(wf_ef4c5e0b,5 agents,固定 G+=27 当分母,只读 OA)**:**recall BEFORE 7/27=25.9% → AFTER 13/27=48.1%,precision 双臂 100%、cry-wolf 0**。两靶类双双抬:**auth-bypass-literal 2→7**(五类站点清单逮注解白名单/正则/私有常量旁路)、**predicate-audit-dead 1→3**(等价路径审计对账 + 集中守卫旁路;但只覆盖该类「审计不等/守卫发散」子口径,「死谓词/僵尸守卫/不可区分」4 条仍 0,**那 4 条本就属 dead_guard/no_producer 别的 finding_kind、非 divergent 口径**)。newly_caught 8(G-AU-01/03/05/09 + G-PC-02/04/12/13)。verdict=fold_lifted。
  - **诚实(2 条真回退 = 下一靶)**:AFTER 漏了 BEFORE 逮到的 **G-PC-10**(confirmAny/rejectAny 缺主态/终态守卫,2-C guard 类)+ **G-PC-15**(unlock 验签锚 vs 去重锚异源,form-a 身份键发散)——新锚把 unlock/confirm 笔墨吸去审计链 + 守卫旁路,丢了这两条 = **加锚的注意力稀释风险**(070 检测法越来越长)。lost(2) << newly(8) 故净强升,但这两类是 AFTER 盲点、值回归。其余诚实:单域 n=1、单采样 LLM 噪、严苛「一 finding 配一 gid」口径下 after ≈40.7%(方向不变幅度收窄)、G+ 本身可能漏(分母偏小、真实 recall 更低)。
  - **裁定**:棘轮 detect→fold→verify 又跑通一整圈、真实 recall 增益(25.9→48.1%,零 cry-wolf);两靶类成功,坐实「补 predicate-audit-dead 审计不等/守卫发散 + auth-bypass 反查」是对的下一步(✅续7 的处方)。下一轮真靶:① 回归 G-PC-10/G-PC-15(2-C guard 缺类 + form-a 身份键异源,防注意力稀释)② 余 dead-code 子类归 070 别的 finding_kind 另测。产物 `_apply-recall-fix2/FOLD-verify-2026-06-26.md`。

- **✅续9(2026-06-30 跨技能泛化首测:070→045,wf_93f4f39e-845 / 7 agents / 940K tok)——把棘轮搬到第二个技能,结果是「弱正向 + 度量法 bug」**:
  - **问题**:070 上跑通的 detect→fold→verify 找全率棘轮,换到 045(api-error-code-design)还成立吗?045 的 R10(跨同族错误码一致性)规则 06-24 折进、仅 dogfood 自评(4/4),从未盲验。A/B 唯一变量=045 SKILL.md(OLD=折前 foldbak 无 R10 / NEW=折后工作树 R10+扫描锚);G+ 建在 OA `ErrorCode.java`(4257 行)+ 4 模块表,ref `03a891375` 只读;3 镜头建 G+(A 族状态分叉/B 命名基数残留/C 声明vs实抛)→ 盲 OLD/NEW 两臂 → 打分。
  - **机械结果**:**verdict=flat,两臂 recall 都 0/17(held-out 0/13)、precision 双臂 100%、cry-wolf 0**。G+=18 全复核 verified=true。
  - **但 flat 是假信号(度量缺陷)**:G+ 和两臂在同一个 4257 行平表里**找了不重叠的区域**——G+ 穷举的是「前置未就绪/状态非法/窗口过期/声明vs实抛」族,两臂(连 NEW)实际扫出的是另一批(线码撞名/自由文本长度码分叉/not-found 异类/TOTP 签名人数残留/onboarding 业务码塞状态位)。各找各的角落 → 对着 G+ 都打 0。**根因 = 棘轮度量法在大平表上的 bug:070 复验能判别是因 held-out 区域小而聚焦(bonus_i1 两区)、G+ 与两臂自然重叠;045 单个 4257 行平表 + 每臂仅 ~6 finding,撞同一缺陷概率太低。学习:大平表复验必须把 G+ 建设与两臂搜索钉死在同一有界子区域(同组族/同行段),否则 recall 测不出差异。**
  - **撇开坏数字能读的(全 ref 复核、两臂零误报)**:NEW 比 OLD **多挖 4 条真缺陷**(自由文本 400/422 族分叉 / SALARY_ADJUST not-found 404vs500 / **DUAL_TOTP 名说双签实则三签 TripleTotpAspect.java:92=held-out GP-B01/B02 同类** / ONBOARDING 40019 塞状态位)、OLD 多挖 1 条(*_ERROR 命名纪律,非 R10),净 NEW +3;但 NEW 两条头部命中(HC_LIMIT/SSC_REROUTE 线码撞名)与 OLD 既有 R09 **逐字重复 = R10 在此冗余非增量**。
  - **裁定**:**不能盖「R10 已在 045 泛化」章(找全率 delta 测量失效);能说「R10 是干净的温和增量、非死重」**(开火、+3 真缺陷集中 R10 目标类含一条 held-out 同类、零 cry-wolf,代价是部分重叠 R09)。**最值钱产物 = 度量法 bug**(070→045 迁移才暴露,070 小聚焦区域掩盖了它)。诚实:单域 n=1、单仓单 ref、LLM 单采样噪(NEW 6 vs OLD 3 跑跑会变)、G+ 已证不完整(两臂挖到 6 条真缺陷不在 G+)。
  - **下一步二选一(未自动执行)**:① 聚焦重测——G+ 与两臂钉同一 ~8 族有界子区域取干净 delta(OLD 无任何族一致性规则→结构上族状态分叉应近 0、NEW 应 >0、大概率 fold_lifted),~900K tok 仍 n=1,可顺带纳入 048;② **收下弱正向 + 度量学习,承认棘轮近边际递减(070 八轮+045 一轮),杠杆移回北极星(被堵的 G2 / 真 ship 一个产品)——倾向此**。全量 → `D:/projects/skills-pilot/oa-pilot/generalize-045-R10-2026-06-30.md`。

- **✅续10(2026-06-30 修复重测:钉死同 6 族,wf_a088edb1-f62 / 6 agents / 700K tok)——证伪 ✅续9 的 flat、R10 在 045 泛化为真**:用户选「①聚焦重测」。修复 = 把 G+ 和两臂都钉死在同 6 个中性「拒绝原因」语义族(全表横扫,因 R10 的族是语义的非行号空间的)。
  - **修复生效(本轮首要验证)**:coverage_overlap 从 ✅续9 的 ≈0 → **0.70**(G+ 70% 落在至少一臂出过 finding 的族)。⇒ **✅续9 的「两臂 recall 双 0」确系找错区域的度量 bug,非 R10 失效**。坐实学习:大平表复验 G+ 与两臂须共享同一**语义有界区域**(对 R10 是族、不是行段),否则 recall 测不出。
  - **判别后结果 = fold_lifted**:**held-out 找全率 NEW 6/17=35.3% vs OLD 3/17=17.6%,delta +17.6pp(NEW 翻倍),precision 双臂 100%、cry-wolf 0**。增量结构归因 R10「按拒绝原因聚族再比对协议状态」扫描锚:NEW 独有 GP-01(族3 自由文本全族 12 码 400/422/403)+ GP-03/04/07(族2 前置六向 403/409/423/422/400/200)= **整族级 finding,OLD 逐码 R02/R09 视角产不出**;OLD 只逮单点分叉(GP-02/05/08)。
  - **诚实(强 caveat)**:单域 n=1 单文件;G+ 仅 20/held-out 17、NEW-OLD 只差 3 条绝对命中、单命中拉动约 6pp、噪声大;LLM 单采样;族4 permission(4 gid)族5 duplicate(2 gid)两臂都没碰、这两族 recall 不可判 + R10 触发覆盖没做满;G+ 不完备(3 条 verified 真缺陷 O4 MAKEUP 补卡重复码 400/409 / N4 族6 对象已锁定 409/423 / N5 入职码 40019 塞状态位 漏收 → 真实分母更大、recall 被低估)。
  - **裁定**:棘轮 detect→fold→verify **首次在「第二个技能 + 干净测量」上成立(070→045)**——R10 域内泛化为真,但强度=温和正向、n=1、非强证据。✅续9 的 flat 结论被本轮证伪(是度量 bug)。**下一步**:048(R08 跨工件单一源,结构不同的规则)若也 fold_lifted = 跨「不同种类规则」泛化更强证据;先 scout 其可测性。全量 → `D:/projects/skills-pilot/oa-pilot/generalize-045-R10-REFOCUS-2026-06-30.md`。

- **✅续11(2026-06-30 第二技能 048 R08 泛化,wf_0aaf494c-5e5 / 6 agents / 703K tok)——结构不同的规则也 fold_lifted,但是「从零到有」+ 未饱和**:R08(同一业务值跨不同工件类型复制无单一源)与 R10(错误码注册表聚族)轴完全不同 = 棘轮跨「不同种类规则」泛化的更强测试。沿用 ✅续10 验证过的「钉死同 scope」修复(5 概念类 × 工件类型)。
  - **结果 fold_lifted**:**OLD(无 R08)在 5 概念类里零 finding**(048 折前压根没这条规则、能力完全缺席);**NEW(有 R08)产出 8 条、逐条 git 核实全真、零误报(precision 1.0、cry-wolf 0)**;held-out 找全率 0→2/12=16.7%,delta +16.7pp。2 条命中 G+(拆单 20000 双源 / 报销频控 5 双源),另 6 条是 G+ 没枚举到的真缺陷(请假窗 180/30/24、工单 SLA 4320/240/1440 双 Java 类、USDT 死锁 10/13/15 config+三写死、绩效 S 上限 0.20 且实漂成 0.1、采购档位表双 DDL、区域绑定上限 2 三处)。
  - **关键诚实**:(1)**OLD 零产出 → 对比本质 NEW-vs-空基线**,R08 是把「不产出」变「产出」的填空(比 045 OLD 有 R09 部分覆盖更彻底,但 delta 不是「谁更强」是「有没有这条规则」);(2)**NEW 漏掉唯一训练正例 GP-01**(采购档位金额 Router-vs-ReimbursementService 静默漂移)→ recall_overall 仅 0.154、**折被拉起但远未饱和**;(3)G+ 不完备(8 产出 6 条 G+ 漏收→真实分母更大);(4)R08 跨工件判定带主观(已逐条 git 核 file:line)。单域 n=1、G+ held-out 仅 12、LLM 单跑。
  - **跨技能大图裁定(D-041 线收口)**:棘轮 detect→fold→verify **泛化成立**——在 070(8 轮深炼)+ 045 R10(同类规则,held-out 17.6→35.3%)+ 048 R08(异类规则,0→16.7%)三处,折规则都抬找全率、**零 cry-wolf**。但一致地:**温和、n=1 单仓、绝对 recall 低/未饱和**(R08 连训练正例都漏)。= 方法论已被刻画清楚:「能迁移、不掉精度,但增益小且未饱和」。**够两点干净泛化数据,无需再炼第 3 个技能**;北极星瓶颈在外部(OA G2 被堵)、不在 skill 质量。全量 → `D:/projects/skills-pilot/oa-pilot/generalize-048-R08-2026-06-30.md`。

## D-042 — STATUS.md 重构:覆盖式现状快照(非追加日志)+ _sessions 当历史 + ritual 改「覆盖不追加」+ Stop hook 行数检查(用户 2026-06-25 拍板)

- **日期**:2026-06-25
- **背景**:STATUS.md 涨到 291KB / 378 行,line5 单行 changelog 独占 131KB(45%);SessionStart hook(`.claude/load_memory.py`)每个新 session **整体注入** STATUS(285KB)+ DECISIONS(100KB)= ~414KB,加载慢。用户提两版方案,锁定「第二招」=STATUS 是覆盖式快照、不是追加日志(白板 vs 笔记本)。
- **根因(workflow wf_9fc0fd83,8 agents/455K tok 验证)**:不是缺日历桶(`_sessions/` 已是健康的逐会话日志,51 文件),是**缺修剪/归档纪律**——CLAUDE.md ritual 只命令 update STATUS、从不命令 trim,每次 append、单调增长。`HANDOFF-*.md` 是铁证(上次把现状拉出去单独成文,2 天废、内容回流 STATUS 顶部)。
- **决定**:
  1. **STATUS = 覆盖式现状快照**,固定区块 = 现在做什么 / 在途线程(每条一行 + 细节链接)/ 卡点 / 按需细读指针;永远 ≤ 一屏(~60 行);做完即删或挪进 `_sessions/`。
  2. **`_sessions/` = append-only 历史日志**(已存在,认领之;**不新建第四层日历文件**)。周报/日报 = 输出(生成时读 thread 汇总,不被日推送)。
  3. **进度单一事实源**:**不**向「日→周→月」三处 rollup —— 那正违反本项目自家 048-R08(cross_artifact_single_source_of_truth,reject)= 拿自家平台规则 dogfood 自己的文档系统。
  4. **ritual 改 replace-not-append**(CLAUDE.md L20 已改)+ **Stop hook 加行数/单行大小检查**(机器兜底,因「纪律靠记性」已自证会腐烂)。
- **执行落地**:STATUS 291693B/378 行 → **2346B/30 行(减 99.2%)**,hook 注入每 session 自动少 ~289KB。全量备份 `D:/work/资料/skills/_archive/STATUS-pre-restructure-2026-06-25.md`;line5 changelog 单独归档 `D:/work/资料/skills/_archive/STATUS-changelog-2026H1.md`(**归档非删**,防个别条目未进 _sessions)。`stop_check.py` 提示词已改对新区块名(去掉旧 已完成/待做/最后更新);**行数检查执行逻辑**先被 self-modification 权限守卫拦下、向用户说明后获授权「需要」→ 已接并实测(新 STATUS 放行 / 旧 284KB 触发 BLOAT;>20KB 或 >8KB 单行即提醒)。
- **DECISIONS 注入优化(同 D-042 一并做掉)**:`load_memory.py` 去掉 DECISIONS.md 全注入,改 `decisions_index()` 实时抽 `## ` 标题(45 决策 + 3 段)注入、全文按需 Read(派生、零漂移、守 048-R08)。**合并效果:SessionStart 注入 ~414KB → ~27KB(减 93%)**——STATUS 瘦身 + DECISIONS 索引各承一半。红线「查 DECISIONS 先」靠索引提示 + 按需 Read 守住。
- **不复议**:STATUS 覆盖不追加、`_sessions` 当日志、不做三级 rollup 已立。记忆 [[always-full-file-paths]]。


## D-043 — Head-to-head 首测「skill 产出 vs 人类代码」:方向对、首跑踩过期 PRD 坑(2026-06-30)

- **背景/转向**:用户 2026-06-30 拍板「打磨工具不是目的,要的是工具能实现更好的产出」([[tool-is-means-output-is-end]])。停止磨 recall,改用 head-to-head 直测北极星命题「单兵×skill ≥ 团队产出」:拿 OA 真 PRD 盲生成代码 → 比人类实现。靶=BUG1334 入职 Node2 GM 3 级兜底(设计稿 §1-2 当 PRD,人类基准 `DefaultWflowOrgIntegration`)。workflow `wf_89df8af9-9ff`(6 agents/427K):盲生成(只喂 §1-2、禁访问 OA)→ 设计→实现→045/048/070 自审 → 3 桶对比 → 裁决。
- **机械裁决 `better`,但已作废**:核实发现人类**现在真接线的是 `resolveGmByTargetOrg`(v2)**(`AssignUserParser.java:1195` 调用、配 10+ 用例测试),而我当 PRD 用的设计稿对应 `resolveGmWithFallback` **零调用=死方法**。⇒ **skill 忠实实现了团队已弃用的旧规范**,「skill 9/9 比人类 7/9 完整」是跟死规范比、不成立;人类「2 条 PRD 外」恰是 v2 现行设计(我 PRD 没跟上)。
- **站得住的(spec-无关,可断言)**:① **硬化 skill 自审当场抓修生成阶段自造的真 bug** = 用户命题微观验证:generate 阶段自加 `excludeSelf()` 把 HM 本人剔出 L1(违 §2.1 明写规则 + 错心智模型「本人审本人」,实际入职主体是新人)→ 070 自审识别并删;另含两套 tie-break 收敛成一套(048)、空集 fail-closed(070);5 处自审修复。**= 不是 LLM 蒙对,是质量 skill 当流程纪律挡下已写进代码的 spec 违背。** ② 生成代码工程卫生确实好(单一常量源/一套排序+环防护/fail-closed 不返空审批人),已落 `D:/projects/skills-pilot/oa-pilot/headtohead-bug1334/GmFallbackResolver-generated.java`。
- **守红线打折的**:「人类有 fail-soft 返空坑」是对比 agent 说的,但 v2 是活的带测试代码、我**未独立确认**,按发现器非裁判**不断言人类有 bug**。盲测相似度(生成 vs §3.4 参考实现)大部分可由「§2 本含审计格式/三级规则」解释、倾向收敛非抄,但不能 100% 排除。
- **真正教训(本测最值钱产出)**:**head-to-head 必须先核 PRD 是 current —— 它对应的方法是不是现在真接线那版**(`resolveGmWithFallback` 零调用就是过期信号)。= [[reqclar-check-canonical-first]] 第①门(判现状先核 canonical)在 head-to-head 同款应用,也是 045 第一轮「度量 bug」同类:**测量设计自身的坑又一次靠核实抓出(D-018 诚实纪律)**。
- **裁定**:转向正确(直测产出而非内部指标),但北极星命题「skill ≥ 团队」**本轮未干净回答**(过期 PRD)。下一步二选一:① 用 v2 现行规范(反推自其 10+ 用例测试 / 禅道单)重测、比 v2 活代码;② 换「设计稿方法仍有调用者」的同版 slice 重测。诚实:只静态比、n=1、LLM 单次方差。产物 `D:/projects/skills-pilot/oa-pilot/headtohead-bug1334/RESULT-2026-06-30.md`。

## D-044 — Head-to-head 修正版:skill 比裸 LLM 强在下行卫生、缺上行判断力(2026-06-30)

- **背景**:D-043 首测踩过期 PRD 坑 + 我两次单视角下结论。用户连给三条方法定论(判维度=代码质量+工程判断非 PRD 保真度 [[tool-is-means-output-is-end]];确认问题要多方验证 [[problem-needs-multi-angle-confirmation]];处理真问题 fan out 整条 skill 链)→ 修正重跑 `wf_c71232d2-5c2`:SKILL 臂(skill 方法+045/048/070 自审)vs PLAIN 臂(裸 LLM)双盲生成自 §1-2,judge 代码质量+判断,比人类 v2(判断力标尺),纪律=只有违背明文当场判其余 ≥2 视角。
- **结果(干净、可信)**:**skill_vs_plain=better,skill_vs_human=mixed,排序 人类 v2 > SKILL > PLAIN**。零 explicit_violation(两臂都正确实现 §1-2 锁死语义、无明文违背),2 条 confirmed 全 two_angle_agreement,7 候选守纪律不当结论。
- **两条确认问题**:① **两臂都死抄 §1-2 的 hmEid 驱动链、没识别 #1334 真根因**(hmEid 在入职表单常解不出→L1+L2 同失效→静默降级顶层 L6;人类 v2 改锚 targetOrgId 绕开)= 设计判断缺口、N120-180;② PLAIN 组织上溯缺 visited 去环(只跳数上限)= 健壮性缺口、N190-220。
- **核心发现(下一靶)**:**skill 加持全落「spec→干净实现」的下行卫生,没落「质疑脆弱 spec」的上行判断**。045/048/070 都是结构/格式/防御层,skill 体系**缺一类「输入 spec 单点失败/根因质疑」的设计审视 skill**(该挂 N120-180)——这正是人类 v2 拉开身位那一步,SKILL 只是把脆弱 spec 抄得更工整。
- **诚实**:纯静态、n=1、LLM 单次方差;**SKILL 自称「27/27 验证通过」却零测试源码、PLAIN 反而实交六类路径单测 → 测试证据 PLAIN 反超 SKILL**(skill 臂自审过度乐观苗头)。
- **裁定**:① skill 对裸 LLM 的增量是**真的但窄**(代码卫生/防御),不是凭空打磨——回答了用户「打磨到底有没有用」=有、但只在下行;② 北极星命题「skill ≥ 团队」**当前 mixed**:质量追平、判断力差一截;③ **demand-pull 下一步明确**:补「spec 批判/根因质疑」设计 skill,先用链分析(fan out 整条链定位真缺口、通用优化、排序)处理这个 confirmed 问题。产物 `D:/projects/skills-pilot/oa-pilot/headtohead-bug1334/RESULT-v2-2026-06-30.md` + 两臂代码 `v2-SKILL-arm.java` / `v2-PLAIN-arm.java`。

## D-045 — 链分析引擎首跑:把 D-044 缺口变成「微调两个已有 skill」的通用优化草案(2026-06-30)

- **背景**:D-044 confirmed「skill 缺『识别输入 spec 单点失败 + 根因质疑』能力」。按用户定的方法(给一个问题 fan out 上下游整条 skill 链、读真实内容、确认真缺口别瞎改、起草通用优化、排序)跑链分析 `wf_0049357e-de8`(9 agents/339K):读 7 候选(005/036/038/040/041/053/054)真实 SKILL.md。
- **结果(方法兑现)**:**不是缺一类 skill,是缺两个具体探针;微调两个已有 skill 非造新**。owner=**N130-040 方案评审提问(主)+ N130-038 方案分析/FMEA(协同)**。链分析的价值:朴素答案会只改 040,但它发现 **040 单独改没用——要问的失败模式得 038 先生成(038→040 有 handoff)**,所以两个一起 = 「查整条链别只修正对的那一个」兑现。守纪律没瞎改 3 个非 owner(005 在设计上游禁设计 / 041 纯耦合拓扑 / 053 是负载降级另一轴)。
- **草案(零项目字样、已验证)**:040 加探针 `P11_chain_hangs_on_single_input_key` + 问法映射 + 新小节(a 真实输入分布下单输入 SPOF:该 key 真实解析率多少/缺失时是否全层垮静默落最弱默认/有没有必有字段可改驱动,显式区别 P03 组件宕机;b 根因契合非表面 spec 照抄)。`generic_check_passed=true`、`validation.catches=true`(走泛化反例:P11 触发→生成正是目标三问 + Q2_CHALLENGE,不被 P03 吞)。038 协同补同名 FMEA 失败模式使检测生成式。
- **诚实**:P11 靠评审者识别「整链由一个 key 驱动」,设计藏起来则可能漏触发;根因质疑刻意窄触发防 cry-wolf。
- **裁定**:**demand-pull 闭环跑通一半**——真实问题(head-to-head 抓出)→ 链分析定位 → 通用可入库优化草案。**这是「打磨让产出更好」的实际产出形态**(不是 recall 数字)。下一步二选一待用户拍:① 折进库(040 主 + 038 协同)② 折完**重跑 head-to-head SKILL 臂**验证优化后是否真逮住单点 = 闭环全证。产物 `D:/projects/skills-pilot/oa-pilot/headtohead-bug1334/CHAIN-ANALYSIS-2026-06-30.md`。

## D-046 — P11 折上库 + 闭环验证:弱闭环,折未被干净证明(2026-06-30,ultracode)

- **执行 D-045 的②(折进库 + 闭环验证)**:① 3 视角对抗审计 P11 折(通用性 clean / 完整性 pass / 反臃肿 additive),采纳两处收窄(根因质疑 b 须依附已触发的 a、防满天飞;038 occurrence 取高后仍走 RPN 公式);② **查出 040 的 references(review-consistency-check.md + exact-contract.md)有 probe 封闭枚举**,只改 SKILL.md 会被自己一致性检查拒 → 同步补 P11(= 用本项目自家 048-R08 跨工件一致性修自己的库);③ 应用(备份 `_apply-spec-critique/backup/` + python zipfile,040 改 SKILL.md+2 refs、038 改 SKILL.md,namelist 不变/零项目字样/frontmatter 完好/库恒 157)。
- **闭环重测 `wf_b8472057-e5b`(PRE vs POST 各 2 seed,唯一差异 P11;POST-a 跑挂只剩 3 臂)**:**verdict=closed_weak、loop_closed=false**。
  - **核心判据未成立**:PRE 两臂(无 P11)靠 040 既有 P03 组件 SPOF + Q2_CHALLENGE **也问出了**单输入 SPOF。⇒ P11 在「探针是否触发」维度边际增量小、不能干净归因。pre_fired=2 / post_fired=1。
  - **P11 真增益在「问出后怎么改」**:仅 POST-b 把脆弱驱动键换掉(新增层用入职必有的「目标部门→公司」字段驱动 + 可观测指标 + rejected-alternatives)= 教科书 re-anchor;PRE 只「检测+去静默+升级」没换驱动。但这是工程判断、单 seed、POST-a 挂故 n 实为 1。
- **更深发现(纠链分析原诊断)**:链分析说「040 不问单输入问题」是错的——040 既有 P03/Q2 已会问。**v2 head-to-head SKILL 臂漏 SPOF 的真根因 = 那臂压根没跑设计评审步骤(只有代码卫生自审)**;一旦跑 040/038(连 PRE 都行)就问出来了。⇒ 更高杠杆在 ① 流程把设计评审接进实现流程 ② 实现/设计 skill 要 act-on-surfaced-risk(把风险落成重构而非只升级)。
- **裁定**:**demand-pull 全闭环跑通了形式(问题→链分析→折→上库→闭环复测),但 P11 的价值未被干净证明**(弱闭环 + POST-a flake + 增益是单 seed 工程判断)。又一次靠闭环测试抓出过度乐观(这次纠的是链分析定位)= D-018/[[problem-needs-multi-angle-confirmation]] 诚实纪律第 N 次兑现。**折暂留(clean/无害/可回退),待用户拍**:① 再跑干净的(多 seed+修 flake,聚焦 redesign-delta)拿真判据 ② 保留+转攻「流程接评审 + act-on-risk」更高杠杆 ③ 回退守精简库。产物 `D:/projects/skills-pilot/oa-pilot/headtohead-bug1334/LOOP-CLOSURE-2026-06-30.md`。

## D-047 — 两缺口 demand-pull 前半段:GAP-2(强制改锚)折 as-is / GAP-1(实现接评审)修 2 缺陷再折,待用户拍折/验(2026-07-01,ultracode)

- **执行 D-046 的②(转攻更高杠杆缺口)**:用同一 demand-pull 闭环打 D-046 揭出的两真缺口。这次前置一个「其实早覆盖吗」怀疑者 agent,逐轴对源码证真后再起草,专防 D-045→D-046 那种错诊。workflow `wf_7f890002-6d8`(13 agents / 868K tok / 12min)。**两缺口都活过怀疑者(2/2)。**
- **GAP-2(单点风险强制产出改锚设计)· owner=039 唯一产设计者(协同 040、源头 038)**:真缺口=链会侦测/问/升级/加固,就差「产出改过的 S3/S4」这条约束规则无人认领。D-046 陷阱已排除——改锚提问早在 `040:182` 逐字存在(草案不重加它),grep「re-anchor/swap driver/demote」全库 0 命中,新增只是绑定规则。**三视角全 pass**;catches 通过(照抄脆弱 spec 在 R11=reject 挂掉,route_back 重跑 S2/S3/S4;§5b 靠 039 自检、上游评审跳过也触发)。= **折 as-is**(1 可选校准:收窄 §5b「未声明」分支;2 非阻塞核对:标注 040 的 P03、核 038 mitigation 枚举位置)。
- **GAP-1(评审「消费+门禁+前送」)· owner=058 主 + 040/039 协同**:真缺口=3 根断线(058 输入无评审槽位只落可选层被降级 / 无自检+就绪规则查评审状态 / 040 订阅=[N330,N340] 结论从不到实现)。逐轴对源码证真(058 只从 N130 取 name/layers/modules/stack、不读 FMEA/评审)。**cry-wolf 揪出 2 必修缺陷**:① 058 就绪词表分裂——权威枚举 `shared-codegen-enums.yaml` 无 constrained/pass,草案全程用它 = 非法、POST 会 StructuredOutput flake;修法用 `contract_aligned` 表达压级。② 嫁接进 R09/READY-000 的 GAP-2 改锚附加款只在问题被打标「确认单点」时触发,但**无 skill 自动产出该标签**(040 发 probe id+criticality 不发布尔)→ 照抄臂上退化成侦测即上报 = 判不足;修法摘掉附加款、GAP-1 保持纯消费+门禁+前送,GAP-2 强制归 039 侧。= **修完 2 处再折**。
- **诚实**:n=1 单 spec/单案例,泛化框架成立+占位符干净但校准未证;可核项(3 断线/040:182/规则号空位)与工程判断项(插入点/cry-wolf 平衡)已分开标。两缺口无一 reject。
- **裁定 · 待用户拍(3 选 1)**:①(荐)先把两草案(GAP-2 as-is + GAP-1 修完)注入 head-to-head SKILL 臂**干跑验证**(PRE vs POST ≥3 seed,主判据 redesign-delta=POST 是否真改锚到必有字段而 PRE 只加固,+ cry-wolf 控制跑干净设计不误触),赢了再折——先证后折、避免又一个 closed_weak;② 直接折(GAP-2 干净 + GAP-1 修 2 处)后跑闭环复测;③ 只折 GAP-2、GAP-1 放。顺序=GAP-2 先(自触发)、GAP-1 后(先解枚举分裂)。**折仍由用户扣扳机(沿用历轮纪律,库恒 157)。** 交付 `D:/projects/skills-pilot/oa-pilot/headtohead-bug1334/FOLD-DECISION-actonrisk-gaps-2026-07-01.md`。

## D-048 — GAP-2 干跑验证(用户选①先证后折):closed_partial,窄而真——delta 仅 1/3、专治时序型脆弱(2026-07-01,ultracode)

- **用户选①**:折前先干跑验证。做法=把草案当规则注入设计臂,PRE(现方法)vs POST(带新规则)×2 样本,3 脆弱 seed + 2 干净对照,2 独立评委(中立分类 + 对抗反驳)判 redesign-delta + cry-wolf。臂走自由文本、只评委用小 schema → 避开 D-046 那次 POST-a 的 StructuredOutput flake。
- **v1(wf_3fabba80,26 agents)= 我 seed 设计漏底、作废**:spec 里写了「X 常空、Y 必有」的 NOTE = 把脆弱键+改锚目标直接喂给臂,删掉了真正要测的「**发现**隐藏脆弱性」难点 → PRE 和 POST 一起满分、delta=0。教训:验证 seed 不能把答案 telegraphed,否则测的是「已知后会不会动手」(基线已会)而非「能不能发现」。
- **v2(wf_13e4676b,去泄底、改中性 CONTEXT 逼发现)= 有效**:**loop_closed=false / closed_partial**。POST 5/5 行为正确(3 脆弱全改锚、2 干净零误触=cry-wolf 干净、机制不滥杀),**但改进 vs PRE 只在 1/3 拉开**:
  - **F1(时序型脆弱:字段在库里有、触发那刻还没填=入职表报到前填、此刻无经理)= PRE 真栽(only_hardened,只加固没换驱动)、POST 改锚**。这正是真 bug #1334 的形状(hmEid 入职时点解不出)。
  - **F2/F3(粗脆弱:这类单/告警本来就没这字段)= PRE 自己就靠需求覆盖缺口分析改锚了**,新规则无增量。
  - ⇒ **gap 真但窄:专治时序型脆弱,非 head-to-head 初判的宽**。两评委 30 格判定零分歧(结论稳,但对抗评委没提供额外区分力;纯静态+单样本,别当铁证)。
- **净结论 = 又一次靠验证抓出「增量比初看小」**(接 D-046 P11 closed_weak、v1 PRE 满分,连三轮同一信号)。**这是强信号非坏消息:157 库在设计评审/act-on-risk 轴已近强基线,边际 skill 打磨回报递减** → 按北极星([[tool-is-means-output-is-end]]/[[north-star-solo-leverage]])杠杆该转向真实使用(往 N=3)或别的瓶颈,别再磨这轴。
- **裁定 · 待用户拍(3 选 1)**:①(荐)折 GAP-2 但 folder 诚实标注「delta 仅 1/3、专治时序型」+ GAP-1 先放(本轮未测、别搭便车)→ 转轴;② 造更多 F1 型难 seed 再跑站稳再折;③ 都不折守精简库直接转轴。**GAP-1 无本轮证据,不得以 GAP-2 名义折(否则重犯 fold-and-claim-verified)。** 数据 `.../scratchpad/judge_data.json`(临时件);脚本 `.../workflows/scripts/verify-actonrisk-drafts-pre-vs-post-wf_3fabba80-148.js`。
- **round-3 终裁(用户选②:造全时序型难 seed + PRE×2/POST×2 + 对抗评委再跑,wf_7aa0aa62,43 agents/1.55M tok)= DO-NOT-FOLD GAP-2**:**strict delta 0/5**(判据=两 PRE 都没发现+两 POST 都改锚+两评委都同意,无一 seed 达到)。原因一致:T1/T2/T4 PRE 基线**自己就改锚了**(读 CONTEXT、看穿字段触发时点未填、换驱动键),POST 产同一份设计;F1 中立判 PRE「只加固」但对抗评委看 coalesce 代码认定 PRE 也改锚(同码反标)、F1 塌;T3 PRE 1/2、POST 2/2(真但薄)。**cry-wolf 零**(POST 在 C1+C3「时序缺失但兜底本正确」都正确不动手;唯一误触是 PRE 臂 C3-preB→规则反而压住误报)。**越加严越缩水**:v2 的 1/3 在加样本+对抗评委后变 0/5 = 信号被证伪非确认。规则残值顶多「已改锚设计上的完整性/可靠性微调(F1 终端去静默、T3 1/2→2/2)且零误报」= 太薄,不进库,**库保持 157**。
- **正面净结论(北极星相关)**:round-3 真正证明的是**现方法上游判断力已达人类那步**——4-5/5 时序型脆弱它自己就看穿并换驱动键。D-044「skill 死抄脆弱 spec、缺上游判断」**更像该次单样本方差,非系统缺口**。诚实边界:纯静态(无编译/运行)、合成 seed 是我按「时序型」假设自造(可能比真 spec 易)、LLM 有方差——不吹「人类级」,但「无 delta 可折」的决定稳。**连四轮(P11 D-046 / v1 / v2 / v3)增量零到负 → 设计评审/act-on-risk 轴已强基线,边际打磨回报递减 → 杠杆转真实使用(N=1→N=3),别再磨这轴**([[tool-is-means-output-is-end]]/[[north-star-solo-leverage]])。**方法教训**:验证 seed 不能 telegraph 答案(v1 栽在此)+ 折前先证救回一次低价值折(=verify-before-fold 纪律第 N 次兑现)。产物 `.../scratchpad`(临时);脚本 `.../workflows/scripts/verify-actonrisk-temporal-round3-wf_7aa0aa62-01c.js`。**GAP-1 全程未测,若将来要动须独立起证。**

## D-049 — 三连事实纠错 + 新主线「充分利用 OA 全流水线 head-to-head」(2026-07-01,用户连纠)

- **背景**:D-048 后我提议"转轴去 dream_true 起玩具 idea→prod 闭环"。用户连三纠把方向拨正:
  - **① OA 不是"推不动"**(我盯裸 master 指针没动就断冻结,却没 grep 其内容里的 bug 号,还矛盾自己记忆 [[oa-live-n2-candidate]])。live 复验:#2946/#2947/#2949 三条我审计触发的 fix 已在发布 master(#2947 commit 显式「外部审计」);#2972-2978 在途 `feature/master-0625`(领先 master 309 commits、天天推)。教训:叙述真团队"停滞"前先读项目记忆 + grep 目标 ref **内容**而非只看 ref 指针(gate④)。
  - **② dream_true 没 PRD**=你自己单作者仓、只用下游 skills(审计→dev-task→发现器 gate)跑已有代码,非完整 idea→prod、非外部团队。
  - **③ CinemaAI 已废弃**(功能同 dream_true),我唯一的上游切片证据也死了。
  - ⇒ 收回"N=2 已达成"overclaim:活的真实使用只剩 2 切片(OA 检测/外部 + dream_true 下游/自有),**完整 idea→prod 干净实例 0 个**。
- **新主线(用户拍板)= 充分利用 OA,别老依赖别的项目**:用 skill **全流水线 head-to-head** 证「单兵×skill 产出能否**全面超过**一个真 7 人团队的真实产出」——逐阶段问:规避了 OA 的问题没?吸收了 OA 的优点没?PRD/架构/代码/完整性/测试逐项更优没?这是 [[tool-is-means-output-is-end]] 的终极检验,且在**真系统**上(非玩具),红线内(读 OA、产物落 skills-pilot)。之前一直只用 OA 做"检测/审计"1 片 + 1 次 tech-solution slice(B3),远没用满。
- **首靶 = 认证/双签(用户选)**:TOTP 重置 + L6 同级双签(RequireDualL6Totp/RequireTripleTotp)。真 PRD(APR-A1-003 v2.5·跨 7 ADR 硬化·防共谋三链会签/签署独立性/降级状态机)+ 真代码(TotpServiceImpl 等)+ 真测试 + 真 bug(#2948/2972/2973/2974/2977/2978)俱全,"问题规避了吗"能直接验。**Stage 1 = Path A 需求→PRD head-to-head 在跑(wf_20899a20)**:非泄底种子 + 4 独立对抗评委三轴(完整性/问题规避/优点吸收)+ 魔鬼代言人替 OA。产物 `D:/projects/skills-pilot/oa-pilot/oa-h2h-auth/`。后续 stage:Path B 架构 / Path C-D 代码 / 测试。

## D-050 — OA head-to-head 前两阶段:结论分化 = skill 在代码安全逻辑赢、在硬化 PRD 输;杠杆按"组织知识密度"分层(2026-07-01)

- **两阶段实测(认证/双签模块,均盲测 + 4 对抗评委 + 魔鬼代言人)**:
  - **Stage 1 Path A(需求→PRD,wf_a5fcfbeb v2 盲)= skill 不能超过 OA**:魔鬼裁 oa_clearly_better。skill 盲版能独立推出整条承重安全架构且诚实标开放问题不瞎编,但组织拓扑绑定(会签角色码/序列落点)+已定政策值(SLA/年限)+ADR 溯源是护城河、结构性(接触不到活体迭代史)、非磨 skill 能补。**方法坑**:v1 REDLINE 把 OA PRD 喂 skill-arm=污染作废(同 D-048 seed 泄底类)——对比/验证输入绝不能带答案。B2 禁 dev 后门 skill 盲版漏=demand-pull 候选(单样本别急折)。
  - **Stage 3 组件1 Path C-D(双 L6 互签守卫代码,wf_bda80d50)= skill 超过 OA 生产代码**:三正向轴(正确性/安全/质量)一致 skill_better、魔鬼 genuine_parity。**决定性:skill 从"两个真正独立当事人"需求自主推出 OA 生产代码缺失的自然人级独立性**——OA 只比 eid(DualL6TotpInterceptor L137)、解析了 userId 却不互比(L153-154),同一自然人持两 L6 工号可两边都签、双人管控被架空;skill 比 userId 拒同人 + 写专测。+ 审计/禁用两处更硬 fail-closed。
- **裁定(北极星精化)**:**skill 杠杆按"组织知识密度"分层**——安全逻辑密集/组织知识轻的代码组件 skill 能超人类真实产出(还找出真漏洞);组织拓扑绑定的 spec(PRD)skill 输、且非磨 skill 能补。杠杆模型 = skill 出安全逻辑+代码骨架+找隐藏弱点,人补组织接线+运营权衡+上线整合。**这是首个"skill 产出 > 人类真实生产产出"在真系统上的证据**(接 D-044 单 slice 打平之后)。
- **诚实边界**:单样本单组件、纯静态未接线、skill 交付的是不能上线纯片段(做 20% 分支逻辑甩 80% 整合)、审计硬门是单方面可用性权衡非严格改进。要成结论须复现(下一步 B3 恢复码/B5 失败告警)。
- **衍生真实 OA 观察件**:双签独立性只到工号级 = 走红线(D-018/verify-only):现象+代码证据(L137/L153-154)、非结论、标审计参考、回归点=同一自然人持两 L6 EID 走双签期望被拒、团队判;攒完代码阶段几组件一起交 HANDOFF(同 #2946-2949)。产物 `.../oa-h2h-auth/STAGE1-*.md` + `STAGE3-c1-*.md`。

## D-050 更正(2026-07-01·用户两条反馈 + 活线核对推翻代码阶段"大胜")

- **⚠️ 上面 D-050 说的"skill 在代码安全逻辑超过 OA 生产代码 / 首个 skill 产出>人类真产出证据"= 高估,更正。** 全流水线跑完(+Stage2 架构 parity + C4 HMAC 压测 + Path B)后,两条更正把代码阶段从"3/3 大胜"拨回"大致打平+几条窄小胜":
  - **① 对决基线是陈旧 origin/master(落后活线 feature/master-0625 309 commits)。** 交 HANDOFF 逐条核活线才发现 C1/C2/C3 判 skill 赢的几个 bug OA 已修:B2 dev 后门(加固)/B3 恢复码 TTL 72h→15min(#2973)/B5 冻结无告警→已补 notifyL6Peer(#2977)。那几个"skill 赢"赢在已修旧码上=对当前真码平手。**教训:对决基线必须先对齐活线/canonical,gate④ 也适用于 head-to-head 基线(我漏了)。**
  - **② C1 决定性胜撤销**:用户确认**工号唯一(一人一工号)**→ OA 的 `eid1≠eid2` 本就等价自然人独立,skill 的 userId 检查非优势、C1 该轴回打平。**教训:判"这是漏洞"前先核对方身份模型/canonical(gate①);我压在"一人可多工号"这个未验证假设上。**
- **更正后总答(总记分卡 `.../oa-h2h-auth/TOTAL-scorecard-CORRECTED-2026-07-01.md`)**:全流水线梯度 = **PRD 输(oa_clearly_better)/ 架构打平(parity 偏 code,skill 反超 OA PRD 两维:防重放 nonce+原子密钥轮换)/ 代码大致打平 + 2-3 条窄小胜(失败计数非原子[开发已确认]/恢复码消费非原子/C4 HMAC 全行签名+nonce,均带不能上线片段+可用性权衡折扣)。「单兵×skill 全面超过真团队」不成立、也不接近。** 杠杆模型(温和版)=skill 追平安全逻辑+偶挖窄改进,人补拓扑接线+运营权衡+上线整合=协作分工,非替代/超越。
- **净教训**:两次高估叠加(陈旧基线 + 未验证组织假设)把"追平+窄点改进"吹成"三连大胜";用户"只是部分模块不能算总体"+ 工号唯一 + 核 PRD 三条反馈拨回真相。守 [[reqclar-check-canonical-first]](gate①先核 canonical/对方模型、gate④先对齐活线)+ [[tool-is-means-output-is-end]](诚实报产出、别吹)。**HANDOFF 观察二撤(工号唯一)、观察三开发确认、观察一 PRD 核恢复码未取消(ADR-580)仍活。**

## D-051 — 最硬测试:工具交付「完整功能」的 shortfall 集中在集成+数据流两处(2026-07-02)

- **日期**:2026-07-02
- **背景**:承 07-01 用户拨正——head-to-head 目的是找 skill 优化方向不是给工具打分。选①不跳:给工具一个有界但完整功能(TOTP 重置普通路:申请→HR核验→系统重置→恢复码→重绑),从零做到能编译/功能点齐/接进 hub-oa,逐条 shortfall→skill 方向。基线先对齐活线(fetch 到 `origin/feature/master-0625` `c80a52167`,hub-oa 零改动)。
- **方法**:派子代理当"工具"(严禁读答案模块 `modular/totpreset/`、OA 只读、写只落 skills-pilot),给两份 canonical PRD。产出 32 java/2437 行,对着封存标尺(真模块普通路切片 ~24 文件/~2400 行)独立核。
- **结论(修正上一轮 20/80 悲观说法)**:
  - **工具插件内业务逻辑基本真且对**:五节点状态机+乐观锁、Redis 配额/冻结、SLA 扫描、恢复码 AES+过期、精确错误码、审计、HMAC 回调,还自修 2 个真事务 bug;代码量与真切片持平(非空壳)。**业务逻辑轴已不弱(呼应 D-048)。**
  - **短板集中在跨边界集成**:5/5 集成全桩,含**功能核心动作「真正重置密钥」被桩**(走完流程却没重置)。
  - **两桶分开(防再高估)**:桶A=真缺口(可达却桩)——(1) HR 序列解析整条桩成永远 Y-L4C1,根因是数据模型漏建 `applicantRoleCode` 输入(真模块该分支仅 15 行纯前缀、Y/Z 根本不跨域;J→编制单位真开发用 getBean+反射接上);(2) 真重置/TG 通知桩掉,但 `TotpService`(auth-api)/`UserTotpService`(同插件 login)/`TgMessageSender`(auth-api)全是既有可注入契约,工具却另造门面桩。桶B=实验限制(wflow 发起契约/PC Web 降级归别域 owner,桩得合理,不记缺口)。
- **产出 = 4 条优先级方向(非分数)**:①(最高)集成前先盘目标库已发布契约面(`*-api`/同插件服务/反射逃生口)再决定接还是桩 → Path B + N150;②(高)数据流建模从业务规则反推派生输入字段、不止照抄表单 → N160 + skill 048 data-flow-mapping(棘轮家族内);③(中)交付即产测试脚手架设为完整功能门 → N230-260 + Path D;④(低)安全收尾清单 → N210。
- **纪律**:样本 n=1、单模块单轮单切片,方向是候选清单不是改库指令;真折进 skill 前按 D-048 须先跑出真实 PRE<POST delta。文档 `D:/projects/skills-pilot/oa-pilot/oa-h2h-auth/SHORTFALL-to-skill-directions-2026-07-02.md`。

## D-052 — 方向1(集成契约面盘点)A/B 验证:强 PRE<POST delta,fold-worthy(2026-07-02)

- **日期**:2026-07-02(承 D-051,用户选①先证后折)
- **干预(通用零项目词)**:落任何 integration 桩之前先盘目标库「已发布跨边界契约面」——① `*-api`/契约模块 ② 同模块/同进程可注入服务 ③ 既有跨边界调用范式(DI/门面/getBean+反射/事件);三条都确认拿不到才允许桩。反模式=未盘就默认「跨域=接不上=造门面桩」。拟加进 Path B `prd-to-tech-solution`/N150 集成映射环节。
- **A/B(除干预外全同:同任务/同 PRD/同只读红线/同型子代理)**:PRE=`tool-run-2026-07-02/OUTPUT`(无干预,5/5 集成全桩);POST=`tool-run-2026-07-02-POST/OUTPUT`(仅加干预)。
- **预登记(看 POST 前写死口径)**:主指标=3 个可达集成(HR解析/真重置/TG通知)接实真契约几项,PRE=0/3;阈值 ≥2/3=强 delta 可折。`DIR1-preregister-2026-07-02.md`。
- **结果(独立核,非信自评)**:**PRE 0/3 → POST 3/3**。(a) HR:就地实现 Y/Z/J 前缀分支+注入真 `OaEmployeeRecordApi`,仅持有人反查留桩(真模块此步也交 wflow);(b) 真重置:注入真 `TotpService`+`UserTotpService.bindGoogleAuth`;(c) 通知:注入真 `OaTgPushLogService.recordSingle` 发催办。**4/4 点名契约已回 hub-oa 核实真存在**、全来自 api/兄弟模块非答案目录。护栏全过:红线干净、桶B(wflow/降级)留桩不计负分、业务逻辑无回退(配额/冻结/乐观锁/恢复码全在;少 570 行=复用真契约+不堆门面桩)。次指标(捕获派生输入)POST 亦 ✅。
- **判定**:方向1 **fold-worthy**——真实、非边际(0→3)、机制可归因(干预直接让工具 grep api 模块找到并注入 5 个真契约而非造 5 门面桩)。
- **诚实边界**:n=1 每臂/单模块/一对 A/B;delta 大且机制明确,严格说折前值得再跑一对压方差。折=改已有 skill 加一步,库恒 157 不新增。方向2(数据流反推派生输入)被顺带带出但未单独 A/B,不算已验。
- **文档**:`D:/projects/skills-pilot/oa-pilot/oa-h2h-auth/DIR1-RESULT-delta-2026-07-02.md`。

## D-053 — 方向1 压方差(第二对 A/B):效应真但比第一对小、基线方差大,第一对高估(2026-07-02)

- **日期**:2026-07-02(承 D-052,用户要求折库前再跑一对压方差)
- **做法**:全新独立一对 PRE2(无干预)/POST2(带干预),同任务同红线,与第一对同口径独立核。
- **四次跑合并(3 可达集成接实真契约数)**:PRE1=0/3、POST1=3/3、**PRE2≈2/3、POST2≈2/3**。→ PRE 臂 {0,2} 均值≈1/3 方差大(全距 0→2);POST 臂 {3,2} 均值≈2.5/3 方差小。所有点名契约(含 resetAllChannels/getUserByEid/revokeGoogleAuth)逐个回 hub-oa 核实真存在、无编造、红线四次全干净。
- **关键真相(压方差压出来)**:① 基线**不是**可靠 0/3——PRE2 无干预时自己就用 getBean+反射接实了重置密钥(2/3);「工具总甩集成」是假的、逐次随机。② 第一对 0/3→3/3 **高估效应**,因抽到最差基线 PRE1。③ 干预真实作用=**抬地板到 ≥2/3 + 加深契约发现**(POST2 还挖出 SM4国密≠PRD写的AES、错误码枚举冲突、ADR-580 只revoke GA),效应≈+1.5 点,非质变;四次里带干预从没帮倒忙。
- **判定**:方向1 **directionally fold-worthy 但效应中等**;干预本身是普适良性零风险工程纪律(桩前先盘契约)。**证据 = 方向明确+效应中等+样本仍小(n=2/臂),非铁证。** 待用户拍:A 现在折(推荐·低风险,fold 条目如实记「效应中等/基线方差大/第一对高估」不吹质变)/ B 再压 2-3 对到 n=4-5 钉实效应量。
- **教训**:单对 A/B 会被基线方差骗(第一对抽到 PRE1 最差基线→看着像 0→3 质变);压方差是对的,救回了一次高估。守 [[problem-needs-multi-angle-confirmation]] + [[tool-is-means-output-is-end]]。
- **文档**:`D:/projects/skills-pilot/oa-pilot/oa-h2h-auth/DIR1-VARIANCE-2026-07-02.md`。

## D-054 — 方向1 扩样 n=5:干净分离,效应稳,前两轮判断都被样本量骗过(2026-07-02)

- **日期**:2026-07-02(承 D-053,用户选 B 再压 3 对到 n≈5)
- **做法**:PRE3/4/5 + POST3/4/5 六个并行跑,合前两对。逐个独立核(不信自评),契约逐个回 hub-oa 核实,红线九次全干净。评分:3 可达集成(HR解析/真重置/TG通知),部分接实计 0.5。
- **每次分**:PRE={0,1.5,1.5,0,0.5} POST={3,2.5,3,2}(POST4 被会话额度截断在服务层前=作废,非做得差)。
- **结果**:**PRE 臂 n=5 均值 0.7/3(全距 0–1.5) vs POST 臂 n=4 均值 2.6/3(全距 2–3)= 干净分离,max(PRE)=1.5 < min(POST)=2,九次零重叠。**
- **修正前两轮**:D-052「0→3」= 单点抽到最差 PRE1 过高;D-053「效应中等/基线不可靠」= n=2 噪声(PRE2/PRE3 偏高各被抽中一次)。**n=5 真相居中偏强:+1.9 点且完全分离**;带干预九次没一次退回门面桩、无干预五次没一次达 POST 水平。
- **判定**:方向1 **fold-worthy 置信度较高**。干预(落集成桩前先盘已发布契约面)普适零风险。**下一步 = 折进 Path B/N150**,fold 条目如实记(n=5 PRE 0.7/POST 2.6/干净分离/POST4 额度截断/单模块单维度),不吹 0→3。
- **教训**:**单/双跑都会被样本量骗**——n=1 看着质变、n=2 看着中等噪声,n=5 才见干净分离。压方差(用户坚持的)两次救回误判(一次高估一次低估)。守 [[problem-needs-multi-angle-confirmation]](多跑才算确认)。
- **文档**:`D:/projects/skills-pilot/oa-pilot/oa-h2h-auth/DIR1-VARIANCE-n5-2026-07-02.md`。

## D-055 — 方向1 已折入 041 module-boundary-identification(2026-07-02·用户拍板折)

- **日期**:2026-07-02(承 D-054 干净分离结论,用户「折」)
- **折点**:N140/041 `module-boundary-identification`(跨边界契约识别 skill;coupling inventory 的 `contract_status` 字段是天然桥接点)。**改已有 skill,库恒 157 不新增。**
- **三处通用改动(零项目词,守 [[skills-must-be-generic]])**:① common-failure-modes.md 加 **F9**「integration marked contract-less without a contract-surface inventory」(桩前必盘三源:导出 api/契约模块 / 同进程可注入服务 / 既有跨边界调用范式;推论:手上数据能算的是边界内逻辑不是外部桩);② checklist.md C 加一条(标 contract-less/stub 的跨边界 coupling 须附盘点证据);③ SKILL.md 步骤7 加句(记 contract-less 或桩前先盘已发布契约面并引 F9)。④ CHANGELOG v4.1.0 记证据来源。
- **打包**:zip 无 `zip` 命令 → 用 Python zipfile 从完整解压树重打包;核对 19 文件条目与原始一一对应、零丢零多、testzip OK,仅 4 文件内容变更。
- **诚实标注**:CHANGELOG 的 Evidence 段如实写「single-module, single-dimension」「n=5 PRE 0.7 → n=4 POST 2.6 干净分离」,不吹 0→3。
- **下一步**:方向 2(数据流反推派生输入)/3(测试脚手架)/4(安全收尾)未验,排队;或转真实使用(北极星卡点仍是 idea→prod 完整闭环,非 skill 质量)。

## D-056 — 转向:停排方向2/3/4,开 N=1 完整闭环(自起真内部小工具 skillctl)(2026-07-03·用户拍板)

- **日期**:2026-07-03。承 D-048/D-051 结论(设计评审/skill-质量轴已饱和,边际打磨回报零到负;真正卡北极星的是「0 次干净 idea→prod 完整闭环」),我主动指回 north star,用户拍板**不再在饱和轴排方向 2/3/4**,转开 N=1 闭环。
- **路径选择**:用户在「①自起真内部小工具(单兵全程、零红线摩擦)/ ②借 OA 真 PRD 跑 Path B/C(受只读红线,ship 不由我控)」中选 **①**。这是最纯的完整闭环:单兵 idea→设计→编码→测试→ship,全程走 skill 链,产物本身即「skill 链能否扛真 idea→prod」的证据。
- **题面 = `skillctl`**(库维护 CLI,用户在 pack-only / pack+lint+count / +coverage 三档中选**最富的 +coverage**,以压满 skill 链)。选题面全凭实痛,非编造:本机无 `zip`、D-055 重打包差点丢文件靠肉眼核、CHANGELOG bump 靠记、库恒 157 靠眼、总表 CSV 154≠库 157 三方从未对账、19/157 覆盖无机器可读记录。
- **工作区** `D:/projects/skills-pilot/skillctl/`(自己 pilot 区,合红线;全程只读 `完稿/` 与 `docs/`)。
- **Path A 已完成**:idea 种子(`00-idea/idea-seed.md`)→ 按 N090/022 prd-generation 的 16 节 `n090.prd.v2` 契约产出 PRD(`01-prd/PRD-skillctl.md`)。PRD 抛出 1 个 P0 blocker:coverage 的 reinforced 判定标准/数据源——推荐机读 CHANGELOG `### Evidence` 段(零维护、有磁盘依据),待用户拍后走 Path B。
- **净纪律**:这是 demand-pull 的正解——不再空磨 skill,让真 idea→prod 的 shortfall 反推哪条 skill 要改(D-030)。每完成一个 Path 记录 skill 链「扛住 vs 掉链」的点,作为改进信号。

## D-057 — description ≤25 词标准:benchmark 验证出「智能缩」批量配方(2026-07-03)

- **日期**:2026-07-03。用 skillctl 量全库(19 gold vs 138 plain)砸出系统性缺口:**description 词数**——库自己标准 ≤25 词(041 CHANGELOG v4.0.0),19 个强化包全守(14-24 词),**139/157 超标**(138 plain 均值 70、最长 156;含 security-risk-analysis 38 词的 gold)。三视角同证(库明文标准+19 gold 全守+3.5x 可测差),过 D-048 门槛=非单轶事。
- **做成 skillctl 真门**:lint 的 `DESC_WORD_WARN` 500→25;`lint --all` = 18/157 干净、139 warn。补回归测试。warn 级(非 error)——高同族簇合理超标。
- **用户选「先 benchmark 再批」**。搭路由 benchmark(N300 高同族簇 5 skill:log/metric/trace/anomaly/rca,judge=Agent 子代理不依赖 API key,10 边界 prompt × 3 run × 3 条件):
  - PRE(原长 ~120 词含 NOT-for)= **100%**;POST-v1(裸缩 ≤25 去 NOT-for)= **90%**(边界 #2「无 trace 从日志重建链路」误 route 到 trace);POST-v2(≤25 但**保留区分句**)= **100%**。各 3 run 零方差。
- **验证出的批量配方(可折)**:description 缩到 ≤25 词;**对高同族簇,保留区分最近同族的那一句关键信号**(如 log-analysis 保留"无 trace 时从日志重建链路")即零路由损失。裸砍会回归、智能缩恢复。log-analysis 156→24 词仍 100%。
- **诚实边界**:5-way 簇级路由是全 157-way 的代理;judge=子代理非真 available_skills 路由,但捕捉同族区分力的相对 PRE/POST 足够。低同族域(库大多数)裸缩本就无回归风险。
- **下一步**:按配方分域批量缩——低同族域直接缩(抽一域跑同款 benchmark 兜底)、高同族簇智能缩保留区分句。139 个待批,证据 `_eval/desc-trim-N300/`。
- **✅ 已完成(2026-07-03 同日)**:139 个全部缩到 ≤25 词,`lint --all` = 157/157 干净、0 超标、库恒 157、工具测试全绿。前 4 域(N340/N330/N350/N360,18 skill)逐域 benchmark 100%/100%;其余 31 域 121 skill = 7 个起草子代理按配方 + `apply_all.py` 两阶段机械安全网(条目守恒+testzip+词数门+desc 校验,首跑拦下 4 条超词→缩→全过)。**高同族抽检**:N210 代码质量(8 近邻)16/16×2、N100 需求门禁 12/12×2,零回归。效率权衡(用户「跑完所有域不逐个问」授权):机械网保完整性+子代理配方保区分+高同族抽检,低同族靠配方+机械网+已验域。commit 15abc6d 等多笔,可回滚。
