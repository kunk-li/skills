# Skill Platform 项目 · Claude 上下文

> 这是给"未来 session 里的 Claude"读的第一份文件。请按顺序读完本文件 + ROADMAP.md + STATUS.md + DECISIONS.md,**再开始干活**。

## 我是谁

- 角色:**agent 平台 builder**(写代码 + 设计 skill 系统),不是 PM
- 上周(2026-05 第三周)刚 ship 了一套 155 个 SDLC skill 的 library
- 单兵作战为主,需要时拉 1-2 个工程师陪跑
- 公司里没现成的外部业务方可以做 Pilot

## 工作风格(Anthropic Claude 看这条)

- ⚡ **数据驱动**——讨厌空泛建议,不要"建议你考虑..."
- 🔪 **Punchy 不要 fluff**——直接给结论 + 数字 + 下一步
- 🎯 **不喜欢被问开放选项**——3 个选项可以,5 个就过度
- 🛑 **不要列长 task list**——已经累积太多了,只给我"现在做什么"
- 🤝 **当我开始迷失方向时,主动指回 north star**(不是顺着我跑偏)
- ✍️ **session 记忆 ritual(不要忘,人会忘所以全推给你)**:
  - 每完成一块有意义的工作 → 立即 update STATUS.md(不要等 session 末)
  - session 中如果新决策诞生 → 立即加到 DECISIONS.md
  - 每次 session 结束前 → 在 `_sessions/<date>-<n>.md` 写总结(n = 当天下一个序号)
  - 这些都**不要等用户提醒**——他会忘,你不要忘。Stop hook 会兜底提醒,但被 hook 提醒说明你已经漏了

## 项目是什么

- 一套 155 个 SDLC skill 的 library
  - 路径:`D:/work/资料/skills/完稿/N*/*.zip`
  - 总览:`skills_workflow_v2.md`
  - 节点:N005(反馈)→ N010-090(需求)→ N100(质量门禁)→ N110(交接)→ N120-180(技术设计)→ N190-220(编码)→ N230-260(测试)→ N270-290(发布)→ N300-320(运行/故障)→ N330-360(文档/协同)→ N370-390(平台)
- 5 条 macro skill 路径(see DECISIONS.md D-002):
  - **A** `requirement-to-prd`
  - **B** `prd-to-tech-solution`
  - **C** `solution-to-dev-tasks`
  - **D** `diff-to-pr-ready`
  - **E** `incident-to-postmortem`
- Eval 框架:`_eval/`(eval.py / scorers.py / adapters.py / tasks*.yaml)
- 真实使用案例:CinemaAI(外部 PM 的 PRD → 我的 skill 跑出 41 工件 / 35 skill 应用)
  - 位置:`D:/projects/python/ai_work/video/cinemaai/CinemaAI-PRD/工作产物/`
  - 状态:由 13 人团队实施到 v0.1.0-alpha

## North Star(为什么做这个)

> **N 个小团队 × 1-3 人 × 4-6 周,用这套 skill 系统从产品想法 ship 到生产。**
> 起步 N=1,半年 N=3,一年 N=10。

判断任何动作是否值得做的唯一标准:**它把我推近 north star 了吗?**

## 当前阶段

**Phase 1 · Pilot 1 · Skills Studio(自造 Pilot)**

详见 ROADMAP.md(长期规划)和 STATUS.md(当下状态)。

## 关键文档(按这个顺序读)

1. `CLAUDE.md` ← 本文件
2. `ROADMAP.md` ← 4 阶段长期规划
3. `STATUS.md` ← 现在到哪了 / 立刻该做什么
4. `DECISIONS.md` ← 已做决策(勿推翻)
5. `_sessions/<最近日期>.md` ← 上次 session 总结(增量上下文)
6. `_eval/README.md` ← eval 框架使用(如存在)
7. `skills_workflow_v2.md` ← 155 skill 全景
8. 外部参考:`D:/projects/python/ai_work/video/cinemaai/CLAUDE.md`(CinemaAI 项目自己的 context)

## 绝对不要做的事

1. ❌ 不要让我在已经决策过的事情上重新选(查 DECISIONS.md 先)
2. ❌ 不要给我列 10 个 macro skill / 10 条路径——**已锁定 5 个**
3. ❌ 不要重新论证"是否要做 eval"——已经在做
4. ❌ 不要建议我去发 Claude Skills marketplace——Anti-goal,Phase 2 之后再说
5. ❌ 不要写 README.md 之类的 marketing doc——内部用,不需要

## 应该做的事

1. ✅ 帮我执行 STATUS.md 里的"下一步"(具体那一行)
2. ✅ 跑 eval / 看数据 / 改具体文件
3. ✅ 我跑偏时拉回 north star
4. ✅ **完成工作块后立即 update STATUS.md**(主动,别等)
5. ✅ **session 结束前主动写 `_sessions/<date>-<n>.md`**(主动,别等)
6. ✅ 新决策诞生时立即加到 DECISIONS.md
7. ✅ 如果 Stop hook 给你提醒了 ritual,**说明你已经漏了**——立即补做,并在 _sessions 里 reflect 为什么漏了

## 一些上下文细节

- 我在 Windows + PowerShell(可调 Bash),Python 3.13 via conda(`/c/ProgramData/miniconda3/python.exe`)
- 没有 Anthropic API key 在 env 里——eval 真跑前需要先拿
- CinemaAI PRD 是**外部 PM 写的**,不是我写的——别把 CinemaAI 当我的 Path A 产物
- 我对 fluff / 长篇大论 / "你做得很棒"等套话过敏
