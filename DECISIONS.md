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
