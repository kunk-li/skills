# Status · Skill Platform

> 这份文件**会经常更新**。每次 session 末尾必须 review 是否还准确。

**最后更新**:2026-05-29(session 2 结束)

---

## 当前阶段

**Phase 1 · Pilot 1 · Skills Studio · Week 0 → Week 1**(刚锁定方向,还未启动 Week 1)

## 即将做的事 ← LOOK HERE FIRST

**触发 Skills Studio Week 1:用 Path A 写 Skills Studio 的 PRD**

### 启动命令(下次 session 直接用)

```
我要启动 Skills Studio Pilot 的 Week 1。
用 requirement-to-prd macro skill 给 Skills Studio 写 PRD。

输入(一句话需求):
"Skills Studio 是一个 Web UI,给小团队浏览、搜索、调用 155 skill 系统,
带 telemetry 看板和 eval 集成。1 人 6 周 ship 到 internal prod。
目标用户是公司内部 1-3 人的小产品团队。"

期望产物(4 份):
1. context-brief.md(背景/假设/开放问题)
2. breakdown.md(5 层 ~25-40 叶节点)
3. PRD.md(16 节)
4. review-agenda.md(评审议程)

存到:D:/projects/.../skills-studio/工作产物/ 下(目录待定)
```

### Week 1 完成判据

- [ ] 4 份产物存到磁盘
- [ ] PRD 通过自我评审(用 path A 的 review-agenda 自检)
- [ ] 跟 STATUS.md 里的 Skills Studio 范围对齐

---

## 已完成(Session 1 · 2026-05-29)

### 战略层
- [x] 锁定 north star(N 团队 ship 产品)
- [x] 4 阶段 roadmap 写完(ROADMAP.md)
- [x] 6 条关键决策记入(DECISIONS.md)
- [x] 锁定 Phase 1 = Skills Studio 自造 Pilot

### 工件层
- [x] cheatsheet(5 路径覆盖 90% 工作)— 在 session 1 transcript,需 condense 到独立文件
- [x] 5 macro skill SKILL.md 草稿 — 在 session 1 transcript,**未存盘**
- [x] 13 个 skill description 改写示例 — 在 session 1 transcript,**未存盘**
- [x] N390 telemetry schema — 在 session 1 transcript,**未存盘**

### 代码层(已存盘)
- [x] `_eval/eval.py` — 主运行器
- [x] `_eval/scorers.py` — 5 维评分(含 gt_similarity)
- [x] `_eval/adapters.py` — Mock + Claude
- [x] `_eval/tasks.yaml` — 25 合成任务
- [x] `_eval/tasks_cinemaai.yaml` — 30 真实 ground-truth 任务
- [x] `_eval/cinemaai_eval_builder.py` — 工件→eval 转换器

### 验证层
- [x] Eval mock 跑通 25 合成任务(format 维度故意低,符合预期)
- [x] Eval mock 跑通 30 ground-truth 任务

### 自动化层(session 2 新增)
- [x] `.claude/load_memory.py`:SessionStart hook 用的项目记忆加载器(读 CLAUDE.md / ROADMAP.md / STATUS.md / DECISIONS.md / 最新 _sessions/)
- [x] `.claude/settings.json`:注册 SessionStart hook
- [x] Pipe-test 通过(20KB JSON,13KB context 注入)
- [x] Auto Mode 拦了"自己验证自己写的 hook"——是正确的安全设计,已说明
- [ ] **用户需要执行**:`/hooks` 重载 或 重启 Claude Code,新 session 才生效
- [ ] **用户需要验证**:新 session 第一句应该直接告诉用户"下一步"(不再问)

---

## 待做(按 ROI 排序,不是 timeline)

### 🔴 P0 · 立即做 / Week 1

- [ ] **Skills Studio Week 1:Path A 跑 PRD**(详见上方"启动命令")
- [ ] 把 5 macro skill SKILL.md 从 session 1 transcript 抠出来存到 `macro_skills/` 目录
- [ ] 决定 Skills Studio 项目目录在哪(候选:`D:/projects/skills-studio/`)

### 🟠 P1 · Week 1 期间穿插做

- [ ] 装 anthropic SDK(`/c/ProgramData/miniconda3/python.exe -m pip install anthropic`)
- [ ] 拿 ANTHROPIC_API_KEY 设到 env
- [ ] 跑 eval baseline:**先 1 个任务**(`eval.py --adapter claude --only CINEMA-N070-requirement-breakdown`)
- [ ] 看 baseline 结果决定是否值得继续做 description 改写

### 🟡 P2 · Week 2+ 再说

- [ ] 13 个改写过的 description 套用到对应 SKILL.md
- [ ] N390 telemetry schema 真落地(写到 Skills Studio 的 DB schema 里)
- [ ] 把 cheatsheet condense 成独立文件 `CHEATSHEET.md`

### ⚫ P3 · Phase 2 时考虑

- [ ] 找 Pilot 2 外部团队
- [ ] description 全套 155 改写
- [ ] CI 集成 eval

---

## Blocker(必须先解的)

| Blocker | 谁解 | 何时 |
|---|---|---|
| Week 4-5 需要 1-2 个工程师陪跑 | 我自己 outreach | Week 3 必须落实 |
| Anthropic API key 没配 | 我自己拿 | Week 1 期间 |
| Skills Studio 部署到哪不确定 | 我自己决 | Week 3 |

## 开放问题(随时可决,不阻塞主线)

- Skills Studio 用什么栈?(候选:Next.js+FastAPI 跟 CinemaAI 一致 / 或更轻 SvelteKit+Litestar)
- 权限模型?(MVP 单租户 vs 多租户)
- Skills 调用是直接调 Anthropic 还是走自家 proxy?

## 跑偏检测(给未来 Claude)

如果用户开始做这些事,请按 CLAUDE.md "应该做的事 #3" 主动拉回:

- 讨论"再加一批 skill"
- 讨论"重写所有 description"
- 讨论"是不是该转方向"(在 Phase 1 还没完成时)
- 讨论 path D 或 E 的优化(没数据,不优化)
- 讨论 Claude Skills marketplace 发布(Anti-goal)
