# 用好 Codex 的一些实战方法(通用 · 持续更新)

这是一份从 `D:/work/资料/skills/CLAUDE-CODE-TIPS.md` 抽象出来、按 Codex 机制重写的通用文档。目标很简单:任何项目 clone 下来后,照这里建立 `AGENTS.md`、`.codex/config.toml`、hooks、状态快照和验证脚本,就能让 Codex 更像一个稳定工程同事,而不是每次从零开始的聊天窗口。

参考来源:2026-07-22 抓取的 OpenAI Codex manual,重点参考 Best practices、Prompting、config、hooks、skills、plugins、MCP、automations 和 multi-agent 相关章节。

配套工具在 `D:/work/资料/skills/_tools/codex-project-kit/`。新项目优先跑:

```powershell
python D:/work/资料/skills/_tools/codex-project-kit/codex_project_tool.py init --root D:/path/to/your/repo
python D:/work/资料/skills/_tools/codex-project-kit/codex_project_tool.py check --root D:/path/to/your/repo
```

## 一、上下文与记忆:让 Codex 每次开局就知道项目规矩

Codex 原生的长期入口不是 Claude Code 的 `CLAUDE.md`,而是 `AGENTS.md`。它会按项目目录向上/向下发现更具体的 `AGENTS.md`,越靠近当前工作目录的规则优先级越高。

### 1.1 用 `AGENTS.md` 放 durable repo guidance

`AGENTS.md` 只放每次都会影响行为的内容:

- 项目目标和当前阶段。
- 目录结构和关键文件。
- 构建、测试、lint、运行命令。
- 编码、评审、提交和验证纪律。
- 红线和绝不做的事。
- 什么叫完成。

不要把长历史、长决策、长日志全塞进去。长文档用路径指针,让 Codex 按需读。

### 1.2 用四类项目记忆文件起步

所有项目都可以用这套最低配:

- `AGENTS.md`:每次自动进入上下文的项目规矩。
- `STATUS.md`:覆盖式现状快照,只写现在做什么、在途线程、卡点、按需细读指针。
- `DECISIONS.md`:只增不改的决策记录,避免重复推翻。
- `_sessions/YYYY-MM-DD-session-N.md`:会话历史,细节放这里,不要堆进 `STATUS.md`。

配套工具的 `init` 命令会自动生成这四类文件。

### 1.3 用 Codex `SessionStart` hook 注入轻量上下文

Codex 支持 `.codex/hooks.json` 或 `.codex/config.toml` 里的 lifecycle hooks。项目被 trust 后,项目本地 `.codex/` hooks 才会运行。适合放两类 hook:

- `SessionStart`:生成轻量上下文,比如 `STATUS.md` 全文、`DECISIONS.md` 标题索引、最近 session 摘要。
- `Stop`:检查收尾 ritual,比如状态快照是否更新、是否写了 session 总结。

重点是轻量。大决策文件只注入标题索引,全文按需读。Codex hook 输出有模型可见长度限制,别把几十 KB 文档硬塞进去。

### 1.4 上下文分层,别把项目规则污染成全局规则

通用个人偏好放 `~/.codex/AGENTS.md` 或全局配置。项目规则放项目根 `AGENTS.md`。子目录特殊规则放子目录 `AGENTS.md`。项目配置放 `.codex/config.toml`,个人默认放 `~/.codex/config.toml`。

范围越小,规则越具体;范围越大,规则越克制。

## 二、配置与工具:把稳定行为固化下来

Codex 的持久化控制面主要是 `AGENTS.md`、`.codex/config.toml`、hooks、skills、plugins、MCP、automations。

### 2.1 用 `.codex/config.toml` 放项目级配置

项目配置只放项目行为,不要放会改变账号、provider、telemetry、profile 的用户私有配置。官方限制里,项目 `.codex/config.toml` 不能覆盖 provider auth、base URL、profile 等用户级敏感项。

建议项目配置只包含:

```toml
[features]
hooks = true
multi_agent = true

# 项目本地规则靠 AGENTS.md,工具调用护栏靠 hooks.json。
```

模型、provider、个人权限偏好放 `~/.codex/config.toml`。

### 2.2 用 hooks 做确定性检查,不要靠人记得

适合 hook 的事情:

- 会话开始时加载项目上下文。
- 每轮结束时提醒更新 `STATUS.md` 和 `_sessions/`。
- shell 或写文件前拦危险命令。
- 工具执行后检查输出是否触发项目红线。

不适合 hook 的事情:

- 需要产品判断的取舍。
- 需要人工审批的外部动作。
- 模糊的“质量感觉”。

配套工具生成的 `.codex/hooks.json` 默认只启用 `SessionStart` 和 `Stop`,属于低风险提醒型工具。

### 2.3 用 kit 初始化所有项目

本仓提供通用初始化工具:

```powershell
python D:/work/资料/skills/_tools/codex-project-kit/codex_project_tool.py init --root D:/path/to/repo
```

它会生成:

- `AGENTS.md`
- `STATUS.md`
- `DECISIONS.md`
- `CODEX-GOVERNANCE-PLAN.md`
- `_sessions/`
- `.codex/config.toml`
- `.codex/hooks.json`
- `.codex/hooks/session_start_context.py`
- `.codex/hooks/stop_ritual_check.py`
- `docs/code_review.md`

生成后在 Codex CLI 里用 `/hooks` review 并 trust 新 hooks。

## 三、提示与协作:让 Codex 少猜、快做、做完

### 3.1 默认提示四件套

重要任务的 prompt 尽量包含四块:

- Goal:要改什么或产出什么。
- Context:相关文件、错误、设计、约束。
- Constraints:哪些不能动,哪些规则必须守。
- Done when:完成判据,比如测试通过、行为变更、文档落盘。

短任务可以一句话,复杂任务必须给完成判据。

### 3.2 复杂任务先 Plan mode

需求模糊、代码面大、风险高时,先让 Codex 计划。Codex 支持 Plan mode,适合先读上下文、问少量关键问题、形成执行计划再动手。

不要把 Plan mode 当会议记录生成器。好计划必须落到下一步具体命令、文件和验证口径。

### 3.3 工作中用 steer/queue 区分插话

Codex 正在工作时,新消息可以 steer 当前 run,也可以 queue 到下一轮。原则:

- 当前方向错了、缺了关键约束:steer。
- 只是后续追加需求:queue。

这样不会把正在跑的验证或编辑打断成半截。

### 3.4 让 Codex 自己收尾,但要给它收尾定义

提示里直接写:

```text
完成前请跑相关测试,检查 git diff,确认没有改到无关文件,并用一句话说明未验证的风险。
```

Codex 能跑测试、看 diff、做 review,但它必须知道项目里“什么算好”。

## 四、日常工程纪律:改动不制造新问题

### 4.1 先摸真实状态再改

每次改代码前默认做三件事:

- `git status --short`
- `rg` 或文件列表定位真实位置
- 读目标文件和相邻模式

不要凭文件名猜架构,不要凭过期行号判断问题。

### 4.2 红线写进 `AGENTS.md`,机械红线再写 hook

例如:

- 只读外部仓。
- 禁止 `git reset --hard`。
- 禁止写入指定目录。
- 文档必须写完整路径。
- 提交只允许显式 add 具体文件。

自然语言红线放 `AGENTS.md`;能机器判断的红线放 `PreToolUse` hook。

### 4.3 git 只显式 add 本次文件

不要用 `git add -A` 兜底。Codex 很容易在工作树里遇到用户改动、生成物、临时文件。提交前只 add 本次真正产物。

### 4.4 外部连接用 MCP/plugin,不要让模型猜私有事实

要读 GitHub、Slack、Drive、Notion、Jira、日历、邮箱,优先用已授权 connector/MCP。没有连接时,让 Codex说明缺口,不要编造“我看过”。

## 五、验证与回归:用证据关门

### 5.1 改前/改后要能比较

真正的改进要有 `PRE < POST`:

- 改前能复现问题。
- 改后问题消失。
- 回归测试仍过。
- 如果不能复现,说明验证边界。

### 5.2 测试之外要真跑

后端改完跑服务或集成测试。前端改完用浏览器/截图/交互验证。脚本改完跑 `--help`、smoke case、错误输入 case。

测试证明逻辑,真跑证明装配。

### 5.3 用 `/review` 和 `docs/code_review.md` 稳住评审风格

把评审规则写进 `docs/code_review.md`,再从 `AGENTS.md` 引用。Codex review 时就能按同一套标准看 bug、风险、回归、测试缺口。

### 5.4 环境假 bug 先排掉

常见假象:

- Windows 终端编码导致中文看似乱码。
- CRLF/LF 被脚本改坏。
- 浏览器缓存让前端看似没变。
- PATH 指到错 Python/Node。
- 当前目录不是项目根。

验证前先固定解释器、路径、编码和工作目录。

### 5.5 判工具好坏看真产出,要比就全量比

评估 Codex、skill、workflow、subagent 或任何生成流程时,不要看二手指标:

- 不看它的自评代替真实产出。
- 不拿别人已经写好的东西替它背书。
- 不用日志漂亮代替功能跑通。
- 不用横切几个点代替功能级全量对比。

正确做法是让工具从真实输入重新跑一遍,拿它自己的产物逐项对比目标行为。要判断“整体能力”,就按功能级全量矩阵比,不要抽几个看起来代表性的点就宣布结论。

Codex 里尤其要防两种偷懒:

- subagent 说“完成”但主线程没有独立抽查产物。
- 生成代码能编译,但核心业务功能没有逐项对团队真码或验收标准比。

结论必须落在“它真做出了什么”和“覆盖了多少项”上。

## 六、复用与大型任务治理:别让多轮工作漂移

### 6.1 反复出现的工作流沉淀成 skill

适合沉淀成 skill 的工作:

- 标准文档生成。
- 代码 review。
- 安全审计。
- 发布检查。
- 事故复盘。
- 跨仓迁移。

skill 放可复用方法和模板,不要塞项目私有事实。项目私有事实仍放 `AGENTS.md` 和项目文档。

### 6.2 插件和 MCP 负责外部能力

选择面:

- Skill:可复用工作流。
- Plugin:可安装的一组 skills、hooks、工具、MCP、assets。
- MCP/app connector:实时外部数据和动作。
- Automation:定时提醒、监控、跟进。
- Subagent:同一任务里的并行分析或并行实现。

别用一个机制包办所有事。

### 6.3 大任务必须有三层治理计划

跨很多会话的大任务,单靠 `STATUS.md` 不够。加一份 `CODEX-GOVERNANCE-PLAN.md`:

- 方向层:目标、完成标准、不可改原则。
- 执行清单层:每项状态和结果。
- 当前位置层:本轮做到哪、下一步是什么。

每次 session 结束覆盖更新“当前位置层”。历史细节进 `_sessions/`。

### 6.4 子代理只做可隔离工作

适合派 subagent:

- 多文件独立审计。
- 多方案并行比较。
- 大仓分区阅读。
- 独立复核结论。

不适合:

- 需要共享同一处编辑状态的细粒度改动。
- 高风险外部写操作。
- 可以主线程 10 分钟内完成的小任务。

派出前把红线写进 prompt,尤其是只读仓、禁止提交、禁止写外部资产。

## 七、多步任务的执行节奏:别急着宣布完成、别空转确认

这是 Codex 最容易在长任务里掉链子的地方:不是不会写代码,而是执行节奏飘。下面四条适用于任何项目。

### 7.1 候选先分真 / 假 / 不确定

审计、排查、review、迁移时,每个疑点都先过一遍:

- 真:进入处理和验证。
- 假:记录原因后丢弃。
- 不确定:保留为待验证,不要当结论。

Codex 可以多找候选,但不能把候选当 findings。尤其 n=1 单点信号,必须先验证再升级。

### 7.2 多阶段任务自动续到底

用户给的是一个完整任务时,Codex 不应每完成一小段就问“要继续吗”。正确节奏:

- 阶段之间自动衔接。
- 只有真分叉、外部副作用、权限越界、需求冲突才停下问。
- 收尾时主动对照完成判据,没全过就继续补。

这条和 Plan mode 不冲突。Plan mode 是先定路,执行时仍要自动推进。

### 7.3 按子节点推进,分波汇报,可随时叫停

大阶段里有多个子节点时,不要一口气跑到不可回头。按子节点推进:

- 一波完成后给短汇报。
- 用户叫停哪个子节点,就停在那里。
- 不抢跑后续子节点。

这适合长链路 shakedown、跨模块迁移、批量 review、全仓治理。

### 7.4 宣布完成前先对照完成判据

不要用“完整 / 全量 / 走完”这类词包装半成品。收尾前先逐条检查:

- 原始目标是否完成。
- 明文完成判据是否全过。
- 验证是否跑了。
- 哪些缺口仍存在。
- 哪些结论只是候选或不确定。

最终汇报先讲缺口,再讲成果。没全过判据,就说“完成了 A/B,还差 C”,不要说“全部完成”。

## 更新记录

- 2026-07-22:初版。按 `D:/work/资料/skills/CLAUDE-CODE-TIPS.md` 的 6 区结构,重写为 Codex 原生机制版,并配套 `D:/work/资料/skills/_tools/codex-project-kit/`。
- 2026-07-22:同步 Claude Code 技巧新增项:加 `5.5 判工具好坏看真产出,要比就全量比`,新增第七区「多步任务的执行节奏」4 条。
