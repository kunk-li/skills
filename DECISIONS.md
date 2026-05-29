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

## 已被推翻 / 修正的决策

(暂无)

**修正决策格式**:
```
## D-NNN-OVERRIDE · <原决策标题>
- **覆盖日期**:YYYY-MM-DD
- **新决定**:<>
- **推翻理由**:<什么数据 / 什么事件让我们改主意>
- **教训**:<下次怎么避免同类错判>
```
