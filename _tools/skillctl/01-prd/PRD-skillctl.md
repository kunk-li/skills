---
artifact_type: prd_document
contract_version: n090.prd.v2
source_mode: from-source
traceability_summary: |
  由 00-idea/idea-seed.md(未结构化需求笔记)生成。所有磁盘事实(157 个 zip、
  zip 内部结构、CHANGELOG 格式、总表 CSV 154 行 GBK、无 zip 命令)均在 2026-07-03
  当场核过。19/157 覆盖率、"恒 157"来自 CLAUDE.md/DECISIONS 叙述,未机器化。
feedback_signals:
  - signal_type: resolved_decision
    related_section: PRD-10
    description: >
      [2026-07-03 实测关闭] "真强化过"判定 = zip 内是否含 CHANGELOG.md。全库扫描证:
      157 个 zip 恰好 19 个含 CHANGELOG.md,与叙述 19/157 分毫不差(连续块 036-054)。
      原推荐的 `### Evidence` 段判定被证伪(只命中 1/19)。数据源已定、无需人工清单。
    target: human review
    severity: resolved
---

# PRD · skillctl —— skill 库打包/校验/覆盖 CLI

## 1. 文档信息与版本说明 [PRD-01]

- 状态:草稿 v0.1(Path A 首稿,待评审)。
- 来源依据:`D:/projects/skills-pilot/skillctl/00-idea/idea-seed.md`。
- 适用评审对象:我自己(单兵 pilot)。这是 N=1 完整闭环的题面,PRD 本身也是"skill 链能否扛真 idea→prod"的证据之一。
- 【明确】本工具纯本机、单人、不上线、不外发、无网络。

## 2. 背景与目标 [PRD-02]

**背景(大白话)**:我维护一套 157 个 SDLC skill 的库,每个 skill 是一个 zip(里面是 SKILL.md、CHANGELOG、references 等)。每次我改进一个 skill,都要:重新打包 zip、确认没丢文件、确认 CHANGELOG 加了新版本、确认库总数还是 157。这些现在**全靠手工 + 肉眼**,已经出过险情(见 PRD-14 的 D-055 事件)。

**本期目标**:做一个本机 CLI `skillctl`,把上述四件手工事自动化,让我下次折 skill 时真的会用它、且它真的能拦下错。

- 【明确】G1:`pack` 能从解压目录重打出与现有 157 个 zip 格式一致的包,并自带条目守恒 + testzip 校验。
- 【明确】G2:`lint` 能检出 SKILL.md frontmatter 缺失、CHANGELOG 未 bump 两类真错。
- 【明确】G3:`count` 能对账磁盘 zip 数 vs 期望 157 vs 总表 CSV 行数,列出缺口。
- 【明确】G4:`coverage` 能列出 157 skill 的 macro 归属/版本/是否强化,给出覆盖率。
- 【明确】非目标见 PRD-03。

## 3. 范围与非范围 [PRD-03]

**纳入范围**:
- 【明确】四个子命令:`pack` / `lint` / `count` / `coverage`。
- 【明确】只读消费 `完稿/N*/*.zip` 与 `docs/*.csv`;所有产物写入自己工作区。
- 【明确】Python 3 单文件或小包实现,标准库优先,零第三方网络依赖。

**明确不做(非范围)**:
- 【明确】不改任何 skill 的内容(pack 只做打包动作,不编辑 SKILL.md)。
- 【明确】不上线、不做 web 服务、不做多用户、不做鉴权。
- 【明确】不碰别人的仓(红线);不写入 `完稿/` 之外我不拥有的任何路径。
- 【推断】不做 CHANGELOG 内容质量评判(只判"有没有 bump",不判"写得好不好")——MVP 边界。
- 【待确认】coverage 若需人工维护"强化清单",MVP 是否含"首次补齐这份清单"未定(见 feedback_signals)。

## 4. 角色与核心场景 [PRD-04]

| 角色 | 目标 | 触发动作 | 关键约束 |
|---|---|---|---|
| 【明确】库维护者(我) | 折完一个 skill 后安全出包 | `skillctl pack <dir>` | 条目守恒、testzip 必须过 |
| 【明确】库维护者(我) | 提交前自检合规 | `skillctl lint <zip\|dir>` | frontmatter + CHANGELOG bump |
| 【明确】库维护者(我) | 确认库健康 | `skillctl count` | 磁盘/期望/CSV 三方对账 |
| 【明确】库维护者(我) | 回答"覆盖率多少/哪些强化了" | `skillctl coverage` | 输出可复查、数字不漂 |

核心场景(端到端):我改完 `041/module-boundary-identification/` 解压树 → `pack` 出新 zip →`lint` 过门 → `count` 确认恒 157 → 周期性 `coverage` 看进度。全程不手写 Python、不肉眼数条目。

## 5. 业务流程 / 页面或能力概览 [PRD-05]

【明确】总览:单一 CLI 入口 `skillctl <subcommand> [args]`,四个子命令彼此独立、可单独调用。无 GUI。

- `pack <src_dir> [-o out.zip]`:遍历解压树 → 规范化条目 → 写 zip → 自检(testzip + 条目守恒)。
- `lint <target>`:定位 SKILL.md 与 CHANGELOG.md → 校验 frontmatter 字段 → 校验 CHANGELOG 顶部版本条目存在且格式合规 →(可选)与内容变更比对是否 bump。
- `count [--expect 157]`:枚举 `完稿/N*/*.zip` → 计数 → 读总表 CSV 行数 → 三方对账 → 报缺口。
- `coverage [--format table|csv]`:枚举全库 → 关联 macro 路径 + 版本 + 强化标记 → 汇总覆盖率。

## 6. 功能需求清单 [PRD-06]

| id | 功能点 | 说明 | 状态 |
|---|---|---|---|
| FT-01 | pack 打包 | 从解压目录重建 zip,顶层目录 = skill 英文名 | 明确 |
| FT-02 | pack 条目守恒 | 与基线(原 zip 或声明清单)比对,文件条目数/名一致,差异即报错退出非零 | 明确 |
| FT-03 | pack testzip | 打完立即 `ZipFile.testzip()`,CRC 坏即失败 | 明确 |
| FT-04 | pack 格式一致 | 路径用正斜杠、可控是否含目录条目、压缩级别与现有 zip 一致 | 推断 |
| FT-05 | lint frontmatter | SKILL.md YAML 头含 name+description,description 词数上限提示 | 明确 |
| FT-06 | lint CHANGELOG 存在 | CHANGELOG.md 顶部有 `## vX.Y.Z (date) — title` + `_skill: <name>_` | 明确 |
| FT-07 | lint bump 检测 | SKILL/references 内容变更时 CHANGELOG 顶版本号必须高于上次 | 推断 |
| FT-08 | count 磁盘计数 | 枚举 `完稿/N*/*.zip`,报总数 | 明确 |
| FT-09 | count 三方对账 | 磁盘数 vs --expect(默认 157) vs 总表 CSV 行数,列出各自差集 | 明确 |
| FT-10 | coverage 枚举 | 列 157 skill:编号/英文名/N 节点/macro 路径 | 明确 |
| FT-11 | coverage 版本 | 从各 zip 内 CHANGELOG 顶部解析当前版本号 | 明确 |
| FT-12 | coverage 强化标记 | 标每 skill 是否"真强化过"(=含 CHANGELOG.md)+ 汇总覆盖率 | 明确(数据源已定案) |
| FT-13 | coverage 输出 | 终端表 + 可选 CSV 导出 | 推断 |

## 7. 业务规则 [PRD-07]

| 触发条件 | 判断逻辑 | 执行结果 | 例外 |
|---|---|---|---|
| 【明确】pack 后条目与基线不符 | 文件条目集合 != 基线集合 | 报差异、退出码≠0、不产出坏包 | 首次打包无基线时以 `--declare` 清单为准 |
| 【明确】testzip 失败 | CRC 校验不过 | 删除半成品、报错退出 | 无 |
| 【明确】lint 缺 frontmatter 字段 | name/description 任一缺 | 标为 error | description 超词数仅 warn |
| 【推断】lint 无 CHANGELOG bump | 内容变更但版本号未升 | 标为 error | 纯格式/空白变更可 warn(需内容 diff 判定) |
| 【明确】count 三方不一致 | 三个数任意不等 | 退出码≠0 + 打印差集 | `--expect` 未给时只报磁盘 vs CSV |

## 8. 状态流转 [PRD-08]

【明确】本工具是无状态 CLI,单次调用即完成,无持久会话状态。每个子命令的内部阶段:

| 状态 | 进入条件 | 退出条件 | 允许动作 | 异常流 |
|---|---|---|---|---|
| 校验入参 | 命令启动 | 参数合法 | 读路径 | 参数非法→退出码 2 |
| 执行 | 入参合法 | 主逻辑完成 | 读 zip/csv、写工作区 | IO/格式错→退出码 1 |
| 自检 | 主逻辑完成(仅 pack) | testzip+守恒通过 | 校验 | 校验失败→删产物、退出码 1 |
| 报告 | 执行/自检完成 | 打印结果 | 输出 table/csv | 无 |

## 9. 权限要求 [PRD-09]

| 角色 | 资源 | 允许动作 | 禁止动作 |
|---|---|---|---|
| 【明确】skillctl 进程 | `完稿/N*/*.zip`、`docs/*.csv` | 只读 | 写/删/改 |
| 【明确】skillctl 进程 | `D:/projects/skills-pilot/`、显式 `-o` 输出路径 | 读写 | —— |
| 【明确】skillctl 进程 | 别人的仓(OA/dream_true 等) | 无 | 一切访问(红线) |

- 【明确】pack 默认输出到工作区或显式 `-o`,**绝不默认原地覆盖** `完稿/` 里的 zip(避免误伤基线)。

## 10. 数据对象与关键字段 [PRD-10]

| 对象 | 字段 | 含义 | 约束 | source of truth |
|---|---|---|---|---|
| SkillPackage | top_dir | 顶层目录=英文名 | 与 SKILL.md name 一致 | zip 内容 |
| SkillPackage | entries[] | 文件条目路径+size | 守恒基线 | zip / 解压树 |
| SkillMeta | name, description | frontmatter | name 非空;desc 有词数上限 | SKILL.md YAML |
| ChangelogEntry | version, date, title, skill | 顶部版本条目 | semver;`_skill:_`==name | CHANGELOG.md |
| LibraryCensus | disk_count, expected, csv_rows | 三方计数 | 期望默认 157 | 磁盘 / CLI 参数 / CSV |
| CoverageRow | id, name, node, macro_path, version, reinforced | 每 skill 一行 | reinforced 判定见下 | 综合 |

- 【明确·2026-07-03 实测定案】**reinforced("真强化过")= zip 内是否含 `CHANGELOG.md`**。全库扫描证据:157 个 zip 恰好 19 个含 CHANGELOG.md,与已知"19/157 真强化覆盖"分毫不差,且为连续块 036-054(N130-170 技术设计节点)。**原推荐的 `### Evidence` 段判定已被证伪**(全库只 041 一个含该段,漏判 18/19)。此定义零额外维护、纯磁盘依据、可机读。副产:`### Evidence` 段可作二级信号标注"经 PRE/POST 验证折入"(目前仅 041),但不作 reinforced 主判据。
- 【明确】macro 路径归属数据源:`docs/节点划分_skill_to_node.csv` + D-002 的 5 条路径定义。

## 11. 异常与边界处理 [PRD-11]

- 【明确】源目录不存在/为空 → 报错退出码 2,不产出空 zip。
- 【明确】zip 内无 SKILL.md 或无 CHANGELOG → lint 报 error 并指名缺哪个。
- 【明确】CSV 编码非 UTF-8(实测为 GBK)→ 按 gbk/gb18030 兜底解码,解不出报明确错误。
- 【明确】`完稿/` 下某 zip 损坏(testzip 失败)→ count/coverage 跳过并列入"损坏"清单,不中断整体。
- 【推断】总表 CSV 有 154 行但库 157 → count 不"修正",只如实列出 3 条差集(哪些 zip 在盘上但不在 CSV)。
- 【明确】并发/重复:单次调用,无并发;重复调用幂等(pack 覆盖 -o 目标前先校验)。

## 12. 非功能与约束 [PRD-12]

- 【明确】运行环境:Windows + Python 3.12/3.13,标准库优先(zipfile/csv/argparse/pathlib);允许极少纯 Python 依赖但**不联网安装的**优先。
- 【明确】安全/红线:进程对 `完稿/` 与别人仓一律只读;写仅限工作区 + 显式 `-o`;无网络调用。
- 【明确】性能:全库 157 zip 的 count/coverage 应在数秒内完成(本地 IO,可接受)。
- 【明确】可复查:所有对账/覆盖数字可用同一命令复现,不依赖记忆(治 idea-seed 痛点 6)。
- 【推断】编码:所有输出 UTF-8;读 CSV 兼容 GBK。

## 13. 验收标准 [PRD-13]

- 【明确】AC-1:对现有某 skill 解压树跑 `pack`,输出 zip 用 `testzip` 通过,且条目集合与原 zip 逐条相等(重打 041 可复现 D-055 的守恒校验)。
- 【明确】AC-2:故意从 SKILL.md 删掉 description → `lint` 报 error;故意改内容不 bump CHANGELOG → `lint` 报 error。
- 【明确】AC-3:`count` 输出磁盘=157、CSV=154,并列出 3 条差集(具体是哪 3 个 skill)。
- 【明确】AC-4:`coverage` 输出 157 行,每行有版本号,汇总出 reinforced 计数与百分比;结果与手工抽查一致。
- 【明确】AC-5:全程无一次写入 `完稿/` 或别人仓(红线),可用 git status 佐证零改动。

## 14. 依赖与风险 [PRD-14]

- 【明确】依赖:`完稿/N*/*.zip` 结构稳定(顶层目录名=英文 skill 名);`docs/技能库总表.csv`(GBK);`docs/节点划分_skill_to_node.csv`。
- 【明确】关键假设:zip 内顶层目录名与 SKILL.md `name` 一致(需 pack/lint 反向校验,不能盲信)。
- 【明确】历史风险实据:D-055 折方向1 重打 041.zip 时 `unzip -l` 报 24 条目 vs 实际 19(差在目录条目计入),靠人肉核对才没丢文件 → FT-02 条目守恒就是治这个。
- 【已消解·2026-07-03】原风险(Evidence 段低估覆盖率)已随 reinforced 定义改为"含 CHANGELOG.md"而消失——实测 19/19 精确匹配,无低估。教训留档:PRD 里"看着合理"的代理指标(Evidence 段)务必先用全库实测证伪/证实再采纳,勿凭直觉写进实现。
- 【推断】风险:pack 格式若与现有 zip 有细微差异(压缩级别/目录条目),diff 会噪 → FT-04 要先逆向现有 zip 的确切格式再定规范。

## 15. 待确认项 [PRD-15]

- 【已关闭·2026-07-03 实测】~~reinforced 判定标准与数据源~~ → 定案 = zip 含 CHANGELOG.md(157 中 19 个,与 19/157 完全吻合)。原 P0 blocker 已消。
- 【P1 / major】coverage MVP 是否包含"首次补齐 19 个已强化 skill 的清单/校准"这件工作(PRD-03)。
- 【P1 / major】FT-04 pack 规范格式:目录条目要不要写入 zip?压缩级别定几?需先逆向现有 157 个 zip 的确切格式统计后定标准。
- 【P2 / minor】FT-07 bump 检测的"内容变更"如何界定(与上一版 zip 做内容 diff?还是仅在用户声明改了内容时校验?)。
- 【P2 / minor】coverage 输出除 table/csv 外要不要 HTML(idea-seed 开放问题)。倾向先 table+csv,HTML 延后。

## 16. 附录 / 参考输入 [PRD-16]

- 输入材料:`D:/projects/skills-pilot/skillctl/00-idea/idea-seed.md`。
- 现场核过的磁盘事实(2026-07-03):`完稿/N*` 下 157 个 zip;样本 `041-module-boundary-identification.zip` 内部结构(SKILL.md/CHANGELOG.md/agents/archive/references/scripts);CHANGELOG 格式 `## vX.Y.Z (date) — title` + `_skill:_` + Added/Changed/Evidence;`docs/技能库总表.csv` GBK 编码 154 数据行、17 列;`docs/节点划分_skill_to_node.csv`。
- 引用决策:D-002(5 条 macro 路径)、D-030(库 157 实数)、D-055(041 重打包条目守恒事件)、D-048(设计评审轴饱和,故此工具价值在真实使用闭环而非再磨 skill 质量)。
- 应用的 skill:N090/022 prd-generation(本 PRD 按其 `references/output-template.md` 的 16 节 n090.prd.v2 契约产出)。
