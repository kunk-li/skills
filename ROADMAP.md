# Roadmap · Skill Platform

> 长期规划。**不要轻易改**。改动需在 DECISIONS.md 留 record。

## North Star Metric

> **N 个小团队 × 1-3 人 × 4-6 周,用这套 skill 系统从产品想法 ship 到生产。**

| 时点 | N | 含义 |
|---|---|---|
| 起步(now)| 1 | Skills Studio 自造 Pilot |
| 6 个月 | 3 | 2-3 个外部团队同时跑通 |
| 12 个月 | 10 | 成为内部 standard tool |

## Phase 1 · Pilot 1(0-6 周)· **改版 see D-004-OVERRIDE**

**目标**:跑通"少量人用 skill 系统 ship 产品"假设的**最小可行证据** —— 直接用,不造壳。

**做什么(改)**:**不造任何工具。** PM(我)出一个**真实产品想法**,用 **agent(团队同款)直接调 skills**,走完整 SDLC:**想法 → 可行性 → 产品(PRD)→ 研发 → 测试 → 部署 → 反馈**。全程在 agent 里产真工件,**边用边记哪个 skill 弱**(= 优化方向,数据来自真用)。

### 流程(每步用真 skill,出真工件)

| 步 | 干什么 | 主要 skill / path | 产物 |
|---|---|---|---|
| **0 · 可行性门禁** | 验想法值不值得做(过了才往下) | N040 痛点 · N050 竞品(**真 web 搜**)· N060 价值/成本/风险 | **go / no-go** |
| 1 · 产品 | 写 PRD | Path A(N030→N070→N090) | PRD 包 |
| 2 · 研发 | 技术方案 + 任务 + 写码 | Path B(N120-180)· Path C · N190-220 | 方案 / 任务 / 代码 |
| 3 · 测试 | 用例 + 质量门禁 | N230-260 | 测试集 + gate |
| 4 · 部署 | 发布 + 验证 | N270-290 | 上线 |
| 5 · 反馈 | 信号回流 + 复盘 | N005 · N300-320 · Path E | 复盘 + 下一轮需求 |

### 完成判据(改)

- [ ] **一个真实产品真 ship 出来**(小没关系),全程靠 skills 走完 SDLC
- [ ] PM(我)在每步都觉得 skill **比白手起家省事**(价值的真检验)
- [ ] 产出一份「**真用中发现的弱 skill**」清单 = 优化方向(真用数据,非合成 eval)
- [ ] 团队同款 agent 能装上这套 skill 直接用(分发可行)
- [ ] 4-6 周走完一个 cycle(超 8 周视为方法论问题)

### 失败模式监控

- 🔴 想法过不了可行性门禁 → **好事**,省了白做;换想法,别硬上
- 🔴 某步 skill 帮不上忙 / 产出没用 → **记下来,这就是优化方向**,别假装有用
- 🔴 走完一圈 PM 还觉得"不如自己干" → 价值假设有问题,stop & rethink(**这次别再用造工具逃避**)

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
