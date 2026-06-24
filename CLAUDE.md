# Skill Platform 项目 · Claude 上下文

> 这是给"未来 session 里的 Claude"读的第一份文件。请按顺序读完本文件 + ROADMAP.md + STATUS.md + DECISIONS.md,**再开始干活**。

## 我是谁

- 角色:**agent 平台 builder**(写代码 + 设计 skill 系统),不是 PM
- 上周(2026-05 第三周)刚 ship 了一套 **157** 个 SDLC skill 的 library(早期约数写 155,D-015/D-019 后实数 157;见 D-030)
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

- 一套 **157** 个 SDLC skill 的 library(真内容强化覆盖只 19/157=12%,demand-pull,见 D-030)
  - 路径:`D:/work/资料/skills/完稿/N*/*.zip`
  - 总览:`docs/skills_workflow_v2.md`
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
7. `docs/skills_workflow_v2.md` ← 157 skill 全景
8. 外部参考:`D:/projects/python/ai_work/video/cinemaai/CLAUDE.md`(CinemaAI 项目自己的 context)

## 🔒 强制红线(每会话必守,不可由子任务/agent/workflow 绕过)

> 用户 2026-06-12 拍板的强制项。任何 session、任何子任务都先守这条。

- **其他项目(OA `hub-oa`/`hub-oa-prd`、dream_true,以及任何不属于本 pilot 的仓)的 PRD 与代码:永不修改,只有查看权限。** 读用 `git show`/`git grep`/`Read`;**绝不改其代码、不写入其文件、不 commit / push / rebase 其分支、不替其提工单**。
  - **澄清(用户 2026-06-23 拍板红线本意)**:红线禁的是「改他人代码 / 写入文件 / 提交 / 推送」,**不是「动 git 状态」这个动作本身**。把本机只读 clone 同步到远端(`git fetch`,或干净工作树上 `git pull` / `git merge --ff-only` 纯快进——不改代码内容、不写文件、不 commit、不 push)**不属禁区,owner 要同步就直接同步**,别再当红线走三轮。基线纪律另算:同步后若工作树 ≠ 目标 ref,审计仍用 `git show <ref>` 对准、不信工作树。
- **写操作只允许落在:本工作目录 `D:/work/资料/skills/` + 我自己的 pilot 产物区 `D:/projects/skills-pilot/`。** 别人的仓一律只读。
- 这条对**子任务、Agent、Workflow 里的 agent、任何形式的任务**一律生效——不能借子代理或工作流绕过(派 agent 前在 prompt 里写明只读铁律)。
- 给别人的改动一律以**文档形式提建议**(可按不同收件人分多份文档),绝不直接改他们的资产。
- **文档编写规则:少符号**(平实叙述,别堆符号/表格/emoji);**问题必须列成「问题点 + 问题出现所在位置」**。
- **第二条红线·详细地址(用户 2026-06-12)**:两层都要做到。
  - **(主)我每次提到/产出一份文档,都要给它的完整文件路径**(它在磁盘上的位置,如 `D:/projects/skills-pilot/oa-pilot/full-audit/01-expense.md`),**绝不只甩文件名**——否则用户得满硬盘找。回复里、清单里、交付时一律写全路径。这是 [[always-full-file-paths]] 的直接执行,我之前漏了。
  - **(次)文档内部引用的问题位置**也要详细完整地址:完整文件路径(从仓库根写全)+ 行号 + symbol,不写类名/方法名/「约 X 行」/裸文件名。**给外部团队的文档**路径相对**收件人自己的仓库根**(让他们在自己 checkout 定位),不用我本机 `D:/projects/...` 绝对路径。
- **第三条红线·不越流程(用户 2026-06-16 拍板·铁律,适用任何外部团队不止 OA)**:对**任何其他团队/项目**(OA、dream_true、任何不属于本 pilot 的外部/生产仓,以及未来任意外部团队)我只有**读取 + 审核**权。产出的是「现象 + 代码证据」**观察件,不是结论**。**是否构成缺陷、严重度多少、要不要立项 → 由对方团队判定;现象成不成立 → 由对方测试确认。** 绝不替任何团队下结论、绝不代提工单(禅道只是 OA 的工单系统,别的团队有别的流程——通则是不代任何人提工单、不越任何团队的审批/测试/立项/发布流程)、绝不说「这是确认缺陷/直接可提工单」。严重度只标「审计参考」;每条观察附一个「供对方测试验证的回归点」(触发条件→期望行为),让测试去确认,而不是我断言它是 bug。= 我是发现器不是裁判(D-018 发现器→人裁定→测试沉淀)。此条对子任务/Agent/Workflow agent 一律生效。教训:违反过两次(「够格单独开禅道工单」「直接可提禅道」)。详见 [[verify-only-no-git-writes]]。

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
- **公司周报/月报固定归档位置**:`D:/work/资料/skills/周报/`(命名 `CD1-2026年第N周周报-Agent板块.md` / `CD1-2026年M月月报.md`)——别落 Downloads 或别处
- **公司日报固定归档位置**:`D:/work/资料/skills/日报/`(命名 `CD1-YYYY-MM-DD-日报-Agent板块.md`,如 `CD1-2026-06-22-日报-Agent板块.md`)——**日报归日报目录,别塞进周报目录**(周报目录只放周报/月报)。教训:2026-06-22 把日报放进周报目录被用户纠。
