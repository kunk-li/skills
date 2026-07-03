---
solution_id: SOL-skillctl-001
version: v0.1
status: draft
derived_from:
  - D:/projects/skills-pilot/skillctl/01-prd/PRD-skillctl.md (n090.prd.v2)
decision_refs:
  - D-002 (5 macro paths → macro_path 归属)
  - D-030 (库 157 实数)
  - D-055 (041 重打包条目守恒事件 → FT-02)
  - D-056 (本 N=1 闭环转向)
produced_by_skill: N130/039 technical-solution-draft-generation (exact-contract)
---

# 技术方案 · skillctl

> 承 PRD-skillctl(Path A)。本稿按 N130/039 的 exact-contract 结构(S1-S6)。
> 关键前置事实均于 2026-07-03 在真库上实测,非假设,见各处标注。

## S1 摘要 [S1_summary]

- **problem_statement**:折 skill 的四件手工事(打包/校验/计数/覆盖)全靠手 + 肉眼,已出险情(D-055 差点丢文件)。要一个本机 CLI 把它们自动化到"我真的会用、真的拦得下错"。
- **proposed_solution**:单一 Python 包 `skillctl`,标准库实现(zipfile/csv/argparse/pathlib),四子命令 `pack/lint/count/coverage`。纯本机、只读消费真库、写只落工作区。
- **key_design_decisions**:
  - `{decision: 条目守恒只比文件条目、忽略目录条目, rationale: 实测 127/157 zip 含目录条目、30 个不含——目录条目是 D-055「24 vs 19」误报根因;只比文件条目才稳}`
  - `{decision: reinforced 判定 = zip 含 CHANGELOG.md, rationale: 实测 157 中恰 19 个含、与 19/157 分毫不差;零维护、纯磁盘依据}`
  - `{decision: pack 输出文件 DEFLATED + 目录条目 STORED + 正斜杠, rationale: 逆向现有库实测格式(compress 8/文件、0/目录,4053 条目全正斜杠)}`
  - `{decision: 标准库零第三方, rationale: PRD-12 约束、无网络、可复现}`
- **expected_outcomes**:下次折 skill 用 skillctl 全程替代手写 Python + 肉眼核;AC-1..5 可复现;至少拦一次真错。

## S2 备选方案 [S2_alternatives_considered]

### ALT-1 打包器实现形态

- **ALT-1a 单文件脚本 `skillctl.py`** — pros[启动零安装、复制即用];cons[四命令堆一文件、测试耦合];scores{complexity: 低, maintainability: 中}。
- **ALT-1b 小包 `skillctl/`(cmd_pack.py 等 + __main__.py)** — pros[子命令分文件、可单测、可长成 coverage];cons[略重];scores{maintainability: 高, time_to_market: 中}。`recommendation: recommended`。
- **ALT-1c 第三方 CLI 框架(click/typer)** — pros[漂亮];cons[**违 PRD-12 零第三方 + 无网络安装**];`recommendation: rejected`;rejection_reason: 违约束。

### ALT-2 条目守恒基线来源(FT-02)

- **ALT-2a 对照原 zip 的文件条目集合** — pros[有真基线、最贴 D-055 场景];cons[首次新建包无原 zip];`recommendation: recommended`(有原 zip 时默认走这条)。
- **ALT-2b `--declare` 显式清单** — pros[首次打包/无基线可用];cons[要手写];`recommendation: acceptable`(无原 zip 时回退)。
- **ALT-2c 不校验、只 testzip** — `recommendation: rejected`;rejection_reason: 治不了 D-055 丢文件。

### ALT-3 lint 的 "bump 检测"(FT-07)

- **ALT-3a 内容 diff:与库中现有同名 zip 逐文件比,内容变了则要求版本号更高** — pros[真自动];cons[要有旧 zip 作基线、diff 有噪];scores{complexity: 高};`recommendation: acceptable`(MVP 后置)。
- **ALT-3b 仅校验 CHANGELOG 顶部版本条目格式合规 + 版本号 ≥ 上一条(库内旧 zip)** — pros[简单稳];cons[改内容忘 bump 且未动 CHANGELOG 时不报];`recommendation: recommended`(MVP 采此,FT-07 降级为"格式+单调"、内容 diff 列入 PRD-15 后续)。

## S3 拟定架构 [S3_proposed_architecture]

- **deployment_topology**:单进程 CLI,本机执行,无服务/无网络/无持久态。入口 `python -m skillctl <sub> [args]`。

components:
- `{component_id: COMP-1, name: cli, responsibility: argparse 解析子命令 + 分发 + 退出码, technology: argparse, interactions: [{with: COMP-2..5, via: sync_api(函数调用), contract_ref: 各 cmd 的 run(args)->int}]}`
- `{component_id: COMP-2, name: cmd_pack, responsibility: 从解压树重建规范 zip + testzip + 条目守恒, technology: zipfile/pathlib, interactions: [{with: COMP-6, via: sync_api, contract_ref: normalize_entries}]}`
- `{component_id: COMP-3, name: cmd_lint, responsibility: SKILL.md frontmatter + CHANGELOG 版本条目校验, technology: 自写 YAML 头解析/re, interactions: [{with: COMP-6, via: sync_api, contract_ref: read_skill_meta/read_changelog_head}]}`
- `{component_id: COMP-4, name: cmd_count, responsibility: 磁盘 zip 数 vs --expect vs CSV 行数三方对账, technology: glob/csv, interactions: [{with: COMP-7, via: sync_api, contract_ref: load_master_csv}]}`
- `{component_id: COMP-5, name: cmd_coverage, responsibility: 全库枚举 + macro 归属 + 版本 + reinforced + 汇总, technology: zipfile/csv, interactions: [{with: COMP-6/COMP-7, via: sync_api, contract_ref: scan_library}]}`
- `{component_id: COMP-6, name: pkglib, responsibility: 公共库——遍历解压树/读 zip 内条目/解析 CHANGELOG 头/解析 SKILL frontmatter/条目集合归一, technology: 纯标准库, interactions: []}`
- `{component_id: COMP-7, name: catalog, responsibility: 读 GBK 总表 CSV + skill_to_node.csv, 提供 skill→node→macro 映射, technology: csv(gbk 兜底), interactions: []}`

## S4 接口契约 [S4_interface_contracts]

### CLI 契约(api_contracts 类比)
- `skillctl pack <src_dir> [-o OUT] [--declare LIST] [--baseline ZIP]` → 退出码 0 成功/1 校验失败(删半成品)/2 入参错。stdout 报条目守恒结果 + testzip OK。
- `skillctl lint <zip|dir>...` → 0 全过 / 1 有 error。stdout 每 target 的 error/warn 列表。
- `skillctl count [--expect 157] [--csv docs/技能库总表.csv]` → 0 三方一致 / 1 不一致 + 打印差集。
- `skillctl coverage [--format table|csv] [-o OUT]` → 0。输出每 skill 行 + 汇总 reinforced/total 百分比。

### 内部函数契约(pkglib / catalog)
- `read_zip_file_entries(zip) -> set[str]`:**只返回文件条目**(过滤 `endswith('/')`),这是守恒比对单位。
- `normalize_entries(src_dir) -> list[(arcname, bytes)]`:arcname 用正斜杠、顶层=目录名;文件 DEFLATED、目录 STORED。
- `read_changelog_head(text) -> {version,date,title,skill} | None`:匹配 `^## v(\d+\.\d+\.\d+) \((\d{4}-\d\d-\d\d)\) .* — (.+)$` + 下一非空行 `_skill: (.+)_`。
- `read_skill_meta(text) -> {name,description} | error`:解析首个 `---...---` YAML 头(自写极简解析,只取 name/description 两键,不引第三方 yaml)。
- `load_master_csv(path) -> rows`:`gbk` 优先、`gb18030` 兜底;返回带 `Skill名称/技能名称 英文/一级分类` 的行。

### 数据契约(db_schema 类比 — 消费的真库结构)
- zip 内布局:`<英文名>/SKILL.md`、`<英文名>/CHANGELOG.md`(可选,存在=reinforced)、`references/*.md`、`agents/*.yaml`、可选 `scripts/*.py`、`archive/*`。
- 总表 CSV:GBK,17 列,154 数据行(与库 157 差 3,count 须如实列差集不修正)。

## S5 需求覆盖矩阵 [S5_requirement_coverage_matrix]

| requirement_ref | 覆盖组件 | 说明 |
|---|---|---|
| FT-01 pack 打包 | COMP-2/6 | normalize_entries 重建 |
| FT-02 条目守恒 | COMP-2/6 | 只比文件条目集合 vs baseline/declare |
| FT-03 testzip | COMP-2 | ZipFile.testzip() |
| FT-04 格式一致 | COMP-6 | 文件 DEFLATED+目录 STORED+正斜杠(实测) |
| FT-05 lint frontmatter | COMP-3 | read_skill_meta |
| FT-06 CHANGELOG 存在/格式 | COMP-3 | read_changelog_head |
| FT-07 bump 检测 | COMP-3 | MVP=格式+版本单调(ALT-3b);内容 diff 后置 |
| FT-08 磁盘计数 | COMP-4 | glob 完稿/N*/*.zip |
| FT-09 三方对账 | COMP-4/7 | 磁盘 vs expect vs CSV 差集 |
| FT-10 coverage 枚举 | COMP-5/7 | skill→node→macro |
| FT-11 版本解析 | COMP-5/6 | read_changelog_head.version |
| FT-12 reinforced 标记 | COMP-5 | 含 CHANGELOG.md(实测 19/157) |
| FT-13 输出 table/csv | COMP-5 | 纯文本表 + csv 导出 |

## S6 风险与约束 [S6_risks_and_constraints]

- **红线**:进程对 `完稿/` 与别人仓一律只读;写仅工作区 + 显式 `-o`;pack 默认**不**原地覆盖 `完稿/` 的 zip。无网络。
- **风险 R1**:pack 目录条目策略——现有库 127 含/30 不含,不统一。**决定**:pack 默认**发射目录条目**(STORED)以贴多数;但守恒比对**只看文件条目**,故是否发目录条目不影响守恒判定,仅影响字节级 diff。文档标明。
- **风险 R2**:read_skill_meta 自写 YAML 解析可能遇多行 description。**缓解**:只需 name + description 单行值,遇复杂结构降级为 warn 不 error。
- **风险 R3**:CSV 154≠库 157,coverage 的 node/macro 映射对那 3 个缺失 skill 会查不到。**缓解**:查不到时标 `node=?/macro=?` 并计入 count 的差集报告,不中断。
- **约束**:Python 3.12/3.13;仅标准库;UTF-8 输出、GBK 读 CSV。

## S7 下游交接(给 Path C 任务分解)

- 建议实现顺序(按"最快兑现真价值"排):COMP-6 pkglib(公共)→ COMP-2 pack(治 D-055 最痛)→ COMP-3 lint → COMP-7 catalog → COMP-4 count → COMP-5 coverage。
- 每步配单测(AC-1..5 是验收锚点);测试脚手架本身也是 dogfood(呼应 07-02 方向3)。
