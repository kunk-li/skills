# Roadmap · Skill Platform

> 长期规划。**不要轻易改**。改动需在 DECISIONS.md 留 record。

## North Star Metric

> **N 个小团队 × 1-3 人 × 4-6 周,用这套 skill 系统从产品想法 ship 到生产。**

| 时点 | N | 含义 |
|---|---|---|
| 起步(now)| 1 | Skills Studio 自造 Pilot |
| 6 个月 | 3 | 2-3 个外部团队同时跑通 |
| 12 个月 | 10 | 成为内部 standard tool |

## Phase 1 · Pilot 1(0-6 周)

**目标**:跑通"少量人 ship 产品"假设的**最小可行证据**。

**做什么**:**Skills Studio** —— 一个 Web UI,给小团队浏览/搜索/调用 155 skill 系统,带 telemetry + eval 集成。

### Week-by-Week

| Week | 干什么 | 产物 |
|---|---|---|
| 1 | 用 Path A 给 Skills Studio 写 PRD | PRD 4 份产物 |
| 2 | Path B:技术方案 + API + Schema | 设计包 |
| 3 | Path C:任务拆分 + 锁定 1-2 个工程师 | Sprint 计划 + 人 |
| 4-5 | 后端 + 前端 + telemetry 接入 | alpha 可跑 |
| 6 | CinemaAI 团队 + 我自用 1 周 | ship 到 internal prod |

### 完成判据(必须全满足)

- [ ] Skills Studio v1.0 可访问(URL / docker / 任意可点的形式)
- [ ] CinemaAI 团队**至少 1 人**真用过(不是给面子的"看看")
- [ ] 至少有 5 次有效 telemetry 数据点
- [ ] 我自己在下次工作时**会主动开 Skills Studio 而不是翻 zip**
- [ ] 6 周完成(超期可宽限 2 周,超 8 周视为方法论失败)

### 失败模式监控

- 🔴 Week 3 还没拿到工程师 → 红灯,缩 Skills Studio scope 到 1 人能干完
- 🔴 Week 4 后端写不出来 → 暴露 N190 代码骨架质量问题,记入 learning
- 🔴 Week 6 没人愿用 → 产品价值假设有问题,**stop and rethink**

## Phase 2 · Pilot 2-3(6-12 周)

**目标**:2-3 个外部团队同时用 Skills Studio,你不陪跑。

**前置条件**:Phase 1 完成判据全绿。

**做什么**:
- 找 2-3 个真实业务团队(可能要花 2-3 周 outreach)
- 每个团队定义自己的 Pilot 产品(20-30 功能)
- 你只做支持,不陪跑写文档
- 收 telemetry + 用户访谈

**完成判据**:
- [ ] 2 个团队真 ship 出来一个产品(不要求大)
- [ ] 至少 1 个团队在你不在场的情况下完整跑过一次 5 path
- [ ] eval baseline → Q1 改进 → Q2 baseline → 看到 metric 提升

## Phase 3 · 自助化(12-24 周)

**目标**:5 个团队同时用,你只看大盘。

**前置条件**:Phase 2 完成判据全绿。

**做什么**:
- 把"陪跑"做的事都产品化(SOP / 文档 / 培训视频)
- 加 onboarding 自动化(新团队进来 1 天就能用)
- N390 telemetry dashboard 真上线
- description 重写完成(155 个全套)

**完成判据**:
- [ ] 5 个团队 monthly active
- [ ] 新团队 onboarding 时间 ≤1 周
- [ ] skill_health_score 90% 的 skill 在 healthy 区间

## Phase 4 · 规模化 or 归档(24+ 周)

**目标**:做决策。

### Branch A · 规模化
- Phase 2/3 数据强 → 扩到 10 团队
- 考虑跨 BU 推广
- 考虑公开发布(Claude Skills marketplace)

### Branch B · 诚实归档
- Phase 2/3 数据弱 → 接受场景局限
- 写完整 case study + post-mortem
- 归档 155 skill,带走 learning

**判断阈值**:Phase 3 完成后,monthly active 是否 ≥5 团队 + adoption 是否还在涨。

## Anti-Goals(明确不做)

| 不做的事 | 何时复议 |
|---|---|
| 发 Claude Skills marketplace | Phase 4 Branch A 后 |
| 重写全部 155 个 SKILL.md | Phase 3 启动时再说 |
| 优化 Path D / E 的 macro(没真实数据) | 真有事故案例后 |
| 给 leader 写 narrative slides | Phase 1 完成后再说 |
| 写 marketing 类 README | 永远不做(internal 工具) |
| 同时做 2 个 Pilot | Phase 1 期间不允许 |

## 北极星偏离警报

如果出现以下情况,**主动告诉我"你跑偏了"**:

1. 我开始讨论"扩大 skill 库"(从 155 到 200+)→ ❌ 不增,只减
2. 我开始优化某个不在当前 Phase 的事 → ❌ 单线推进
3. 我连续 2 个 session 没动 STATUS.md → ❌ 在打转
4. 我开始焦虑"是不是该转方向" → ✅ 这是健康信号,但要看数据再决定
