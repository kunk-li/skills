# SDLC Skills Library · 使用指南

一套覆盖软件研发全流程的 **157 个 Claude skill**。从「用户反馈 / 一个想法」一路到「PRD → 技术方案 → 开发任务 → 代码 → 测试 → 发布 → 故障复盘」,每一步都有对应的 skill 帮你把活干得更快、更全。

这份文档的目标:**你 clone 下来,照着走,就能用,不用再问别人怎么用。**

> 想直接上手、边做边学?看 **[GETTING-STARTED.md](GETTING-STARTED.md)** —— 用一个小功能(用户提现)半天走完整条链 A→D 的实操指南。

---

## 1. 一分钟看懂这是什么

- **是什么**:157 个独立的 skill(技能)。每个 skill 是一段给 Claude 的专门指令 + 配套模板/检查清单,让 Claude 在某个具体环节(比如「生成 PRD」「设计数据库表」「写测试用例」「做故障复盘」)产出专业级草稿。
- **怎么组织**:157 个 skill 按研发流程分成 **40 个节点 / 12 个阶段**,编号 `N005`(反馈)→ `N390`(平台治理),存放在 `完稿/N*/` 目录下,每个 skill 是一个 `.zip`。
- **怎么用**:不是挑单个 skill 用,而是**按你所处的阶段,沿一条链走**(见第 4 节 5 条主路径)。
- **定位**:skill 产出的是**高质量草稿 / 加速器**,不是自动交付物。**必须人审 + 测试验证**(见第 5 节),这是用好它的前提。

---

## 2. 快速开始

### 2.1 下载

```bash
git clone https://github.com/kunk-li/skills.git
cd skills
```

所有 skill 在 `完稿/` 下,按节点分目录,例如:

```
完稿/N090 PRD产出与评审/022-prd-generation.zip
完稿/N160 数据模型设计/046-table-schema-design-recommendation.zip
```

### 2.2 一个 skill 包解压后长什么样

```
prd-generation/
├── SKILL.md            ← 核心:给 Claude 读的指令(name + description + 正文)
├── references/         ← 配套资料:检查清单、输出模板、失败模式、示例输入输出
│   ├── checklist.md
│   ├── output-template.md
│   ├── common-failure-modes.md
│   └── ...
└── agents/             ← 可选:agent 配置
```

`SKILL.md` 顶部的 `name` 和 `description` 决定 Claude 什么时候该用它;正文是它怎么干活的规则。

### 2.3 装进 Claude Code(推荐)

Claude Code 会自动发现 skill 目录里的 `SKILL.md`。把需要的 skill 解压进项目的 `.claude/skills/`(团队共享)或个人的 `~/.claude/skills/`:

```bash
# 以「生成 PRD」为例,解压到项目 skills 目录
mkdir -p .claude/skills
unzip "完稿/N090 PRD产出与评审/022-prd-generation.zip" -d .claude/skills/
```

之后在 Claude Code 里正常提需求(比如「帮我把这份需求笔记生成 PRD」),Claude 会自动调用匹配的 skill。也可以直接用 `/` 唤起。

### 2.4 不用 Claude Code 也能用(兜底)

任何能和 Claude 对话的地方,直接**打开 `SKILL.md`,把内容作为指令贴给 Claude**,再附上你的输入材料即可。`references/` 里的模板和清单可以按需一起贴。

---

## 3. 怎么找到你要的那个 skill

三种方式:

1. **按流程节点找**:看第 6 节的全景表,定位你在哪个阶段,去对应 `完稿/N*/` 目录拿。
2. **按主路径走**(推荐):看第 4 节,选一条链,沿链上的节点依次用。
3. **按关键词找**:`docs/技能库总表.csv` 是全 157 个 skill 的总表(节点 / 中文名 / 英文名 / 功能 / 依赖 / 边界)。`docs/skills_workflow_v2.md` 是带拓扑图的流程全景。

---

## 4. 5 条主路径:按你所处的阶段选一条

不要孤立地抓单个 skill。**先判断你手上有什么、要产出什么,选一条链,沿链走。**

### A. 想法 → PRD(`requirement-to-prd`)
你有:用户反馈 / 一个产品想法 / 零散需求笔记。你要:一份可评审的 PRD。
链路:`N005 信号聚合` → `N010 需求归档` → `N020 去重聚类` → `N030 背景补全` → `N040 用户洞察` → `N050 竞品研究` → `N060 需求评估` → `N070 结构化建模` → `N080 原型解析` → `N090 PRD 产出` → `N100 质量门禁` → `N110 交接验收`
关键 skill:`requirement-breakdown`、`business-rule-extraction`、`permission-matrix-extraction`、`prd-generation`、`requirement-completeness-check`、`requirement-conflict-detection`。

> **这一步最关键**:PRD 的质量直接决定后面所有产出的上限。别急着往下跑,先用 N070 / N090 / N100 把需求逼清楚——边界条件、异常路径、并发、权限,这些是后面最容易出 bug 的地方。

### B. PRD → 技术方案(`prd-to-tech-solution`)
你有:一份 PRD。你要:技术方案 + 架构 + API + 数据模型设计。
链路:`N120 技术需求理解` → `N130 方案分析评审` → `N140 架构边界` → `N150 API 设计` → `N160 数据模型` → `N170 非功能设计`
关键 skill:`technical-solution-draft-generation`、`module-boundary-identification`、`api-design-recommendation`、`table-schema-design-recommendation`、`concurrency-control-recommendation`、`authorization-model-design`、`security-risk-analysis`。

> 这一段(设计 / 评审)是整套 skill **最强、最稳**的部分,能实打实省时间。

### C. 方案 → 开发任务(`solution-to-dev-tasks`)
你有:技术方案。你要:拆好的、可排期的开发任务。
链路:`N180 研发任务规划`
关键 skill:`development-task-breakdown`、`effort-estimation-assistant`、`dependency-identification`、`planning-package-aggregator`。

### D. 代码改动 → 可提 PR(`diff-to-pr-ready`)
你有:要写的功能 / 一份 diff。你要:能过 review、能提交的代码 + 测试。
链路:`N190 代码骨架` → `N200 辅助代码` → `N210 静态检查` → `N220 Code Review / PR` → `N230-N260 测试` →(需要发布时)`N270-N290 发布`
关键 skill:`service-draft-generation`、`transaction-boundary-check`、`thread-safety-risk-check`、`diff-risk-review`、`pull-request-description-generation`、`test-case-generation`、`concurrency-test-point-generation`。

> **代码这一段务必按单个功能切片走,别整包生成**:一次让 skill 出一个切片的草稿 → 人审工程判断 → 写测试确认 → 再下一个。整包直出的代码容易漏并发唯一性、越权、脱敏这类「看着对其实错」的问题。

### E. 事故 → 复盘(`incident-to-postmortem`)
你有:一次线上故障 / 告警。你要:定位、修复评估、复盘沉淀。
链路:`N300 监控日志定位` → `N310 处置响应` → `N320 故障复盘`
关键 skill:`log-analysis`、`root-cause-analysis-recommendation`、`impact-scope-analysis`、`remediation-plan-recommendation`、`production-incident-postmortem`。

---

## 5. 使用纪律:怎么用才产出得好(必读)

**skill 产出是草稿,不是终稿。** 用好它靠三步闭环,缺一不可:

1. **skill 出稿** —— 让 skill 生成 PRD / 设计 / 代码 / 测试草稿。
2. **人审工程判断** —— 人来审它的取舍对不对,尤其是并发、权限、脱敏、异常路径这些高危点。逐行看,别只扫一眼觉得「像那么回事」就过。
3. **测试确认现象** —— 写测试跑一遍,让测试确认它到底对不对,而不是靠肉眼判断。

另外两条经验:

- **输入质量封顶产出质量。** 需求 / PRD 含糊,skill 再好也补不全——它是放大器,不是补全器。想产出好,先把输入写清楚。
- **定位是加速器,不是自动交付。** 把它当「给你一份专业级强草稿的助手」,能省掉大量从零起步的时间;但最终质量由你的人审 + 测试兜底。

---

## 6. 全景速查:40 节点 / 12 阶段

| 阶段 | 节点 | 干什么 |
|---|---|---|
| 反馈回流 | N005 | 线上信号聚合、反馈聚类、数据驱动需求挖掘 |
| 需求输入 | N010-N050 | 需求归档 / 去重聚类 / 背景补全 / 用户洞察 / 竞品研究 |
| 需求定义 | N060-N090 | 需求评估 / 结构化建模 / 原型解析 / **PRD 产出与评审** |
| 需求门禁 | N100-N110 | 完整性·可执行·冲突·漏洞检查 / 交接与验收标准 |
| 技术设计 | N120-N170 | 技术方案 / 架构边界 / API 设计 / 数据模型 / 并发·幂等·权限·安全·性能 |
| 任务规划 | N180 | 开发任务拆分 / 工时估算 / 依赖识别 |
| 编码 | N190-N220 | 骨架生成 / 辅助代码 / 静态质量检查 / Code Review 与 PR |
| 测试 | N230-N260 | 测试设计 / 回归与自动化 / 缺陷管理 / 质量门禁与专项测试 |
| 发布 | N270-N290 | 发布准备与策略 / 配置环境 / 上线验收 |
| 运行与故障 | N300-N320 | 监控日志定位 / 处置响应 / 故障复盘 |
| 文档与协同 | N330-N360 | 技术运维文档 / 经验沉淀 / 协同任务风险 / 跨团队对齐 |
| 平台层 | N370-N390 | skill 路由 / 多技能编排 / 门禁 / 模板治理(元层,给编排用) |

完整 157 个 skill 明细见 `docs/技能库总表.csv`;带拓扑图的流程全景见 `docs/skills_workflow_v2.md`。

---

## 7. 一个真实端到端例子

一份外部 PM 写的产品 PRD,沿路径 A→D 跑这套 skill,产出了 **41 个工件、应用了 35 个 skill**,交给一个团队实施到了 v0.1.0-alpha。说明整条链是能端到端跑通的——前提是按第 5 节的纪律用。

---

## 8. 常见问题

**Q:我该从哪个 skill 开始?**
A:看你手上有什么。只有想法 → 路径 A;已有 PRD → 路径 B;要写代码 → 路径 D;出了故障 → 路径 E。选一条链,沿链走。

**Q:一定要用 Claude Code 吗?**
A:不。Claude Code 能自动发现和调用 skill,体验最好;但你也可以直接把 `SKILL.md` 内容贴给任何 Claude 对话用(第 2.4 节)。

**Q:skill 生成的代码能直接上线吗?**
A:不能直接上。它是草稿,必须人审 + 测试(第 5 节)。把它当加速器,最终质量由你兜底。

**Q:zip 用系统自带工具解压报错?**
A:个别 zip 用某些老解压工具列目录会异常,用 `unzip`、7-Zip 或 Python `zipfile` 都能正常解出。
