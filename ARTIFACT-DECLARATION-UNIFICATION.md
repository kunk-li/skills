# 产物声明统一方案(方案态 · 尚未执行 · 库未改动)

> 产出于 2026-07-20,主线 A1 模块跑到 B-design 之后。用户拍板走 **选项 C:现在只出扫描器 + 迁移方案,不动库**;等 A1 全链跑完、进入 FIND4 阶段再执行。
>
> 取证工具:`.claude/artifact_declaration_scan.py`(`--missing` / `--collisions` / `--migration`)
> 相关候选:`oaval-A1-auth/CHAIN/CANDIDATE-LEDGER.md` 的 CAND-12 / CAND-13 / CAND-15

## 一、为什么要做:一个连作者本人都稳不住的数字

回答「有多少 skill 不声明自己的产物名」时,我**接连扫了三次,得到三个不同的数**:

| 第几次 | 覆盖几种声明形态 | 得出「无声明」 |
|---|---:|---:|
| 第一次 | 7 种 | 25 包 |
| 第二次 | 13 种 | 15 包 |
| 第三次(现固化) | 15 种 | 17 包 |

每一次我都以为穷举完了,每一次都漏。第二次是被跑 N170 的子任务当场指出(它说「这六个包明明写了 `node target:`,你的前置结论错了,建议回查核实方法」),复核证实它是对的。

**一个数字连写脚本的人自己都稳不住,下游任何自动化都不可能稳得住。** 这比任何论证都更能说明问题。

## 二、现状(全库 157 包,机器扫描)

**15 种声明形态在用**,分布极不均衡:

| 形态 | 包数 |
|---|---:|
| `node_artifact_target` | **73** |
| `artifact_target` | 26 |
| `workflow_alias` | 21 |
| `artifact_name` | 12 |
| `primary artifact`(空格) | 12 |
| `primary_artifact` | 6 |
| `node target`(空格) | 6 |
| `Canonical output name` | 5 |
| ``artifact named `X` `` | 4 |
| 其余零星形态 | — |

**每包用几种**:无任何声明 17 包 / 用 1 种 115 包 / 用 2 种 25 包。

## 三、已实测到的真实危害(不是推演)

**① 同一批产物,两条合理推导路径给出两个答案。**
A1 的 B-design 段 19 个环节跑完后:

| | 库内声明了产物名的 9 个包 | 未声明的 10 个包 |
|---|---|---|
| 机器检查器找得到 | **9 / 9** | 5 / 10 |
| 找不到 | 0 | **5 / 10** |

**凡声明零分歧,凡未声明一半对不上。** 找不到的 5 个(041/042/046/047/048)产物全部真实存在、全带契约头(49K~65K),只是执行者按「下游怎么引用」取名、检查器按「输出模板标题」推导,两条路都合理、结果不同。

**② 更硬的一层:生产方与它的直接下游,对同一个文件叫什么名字说法相反(CAND-13)。**

| | 041 该叫什么 | 042 该叫什么 |
|---|---|---|
| 自己包内(SKILL.md / exact-contract / output-template / v2-alignment) | `module_boundary_map` | `service_decomposition_recommendation` |
| **直接下游的 SKILL.md** | 042 明写 `模块边界分析.md` | 043 与 055 按 `服务拆分建议` 消费 |

链是靠文件名连的。**生产方按自己包里的名字落盘,下游按另一个名字去找,自动编排下直接找不到文件。**

## 四、方案

### 4.1 统一目标:一套 schema(三个字段),不是一个字段

**必须保留三元组,只留文件名会抹掉重要语义**:

| 字段 | 作用 | 现状 |
|---|---|---|
| `node_artifact_target` | 产物文件名 | 73 包已在用,定为统一目标 |
| `shared_artifact_role` | `contributor`(多方追加同一产物)/ 独占 | 已存在,**不得合并掉** |
| `aggregation_strategy` | 如 `append_with_skill_prefix` | 已存在,**不得合并掉** |

**为什么必须保留后两个**:072/073/074 三个 skill 都声明 `风险检查清单.csv`,我一度误判为「名字撞车、后写覆盖先写」。查原文后证伪 —— 那是**有意的多贡献者追加式共享**:各自行 ID 加 `npe.`/`txn.`/`tsr.` 前缀防冲突,配 `n210-shared-contract.md` 与 `aggregation-handoff.md` 两份共享契约,由 075 以 `node_aggregation` 模式聚合并作 N210 唯一事件发布者。**设计质量很高。若统一时只保留单一文件名字段,这层语义会被抹掉。**(详见 CAND-15)

### 4.2 迁移分三档

| 档 | 包数 | 处理 |
|---|---:|---|
| **A. 已合规** | 53 | 只用 `node_artifact_target` 一种,无需改动 |
| **B. 需改写形态** | 87 | 把其余 14 种形态改写为 `node_artifact_target`;**原形态删除不保留**(留着仍会被误读) |
| **C. 无声明,需人工裁定** | **17** | 见下,**不可脚本批量生成** |

合计触及 **104 个包**;**库文件数不变,仍恒 157**(改内容不改数量)。

### 4.3 C 档 17 个包(必须逐个人工裁定)

```
0000-product-doc-to-requirements
038-technical-solution-analysis        039-technical-solution-draft-generation
040-solution-review-question-generation
041-module-boundary-identification     042-service-decomposition-recommendation
046-table-schema-design-recommendation 047-index-design-recommendation
048-data-flow-mapping
139-product-engineering-alignment-summary  140-qa-engineering-alignment-summary
141-version-scope-trimming-recommendation  142-project-rhythm-tracking
143-skill-routing-selection            144-context-memory
145-multi-skill-orchestration          146-state-machine-driven-orchestration
```

**为什么不能脚本生成**:CAND-13 已证实下游消费方叫的名字可能与生产方包内的推导名不同。这 17 个必须**逐个查「下游 SKILL.md 是怎么引用它的」再定名**,让消费方期待优先——否则统一完照样断链,只是断得更整齐。

## 五、执行前的门槛(按项目纪律,不可跳)

1. **这是支线折叠**,须先做 A/B:PRE(现状)与 POST(统一后)各跑一次同一批模块,证明 **PRE < POST** 才能折进库。
2. **A/B 的度量已经有现成的**:B-design 那张「声明了的 9/9 找得到、没声明的 5/10 找得到」表就是天然的 PRE。POST 应当是 19/19。
3. **不得破坏库恒 157**:本方案只改文件内容,不增删文件。
4. **必须项目无关**([[skills-must-be-generic]]):统一后的字段语义不得绑定任何具体项目。

## 六、当前状态

- ✅ 扫描器已固化:`.claude/artifact_declaration_scan.py`(15 种形态写死在 `FORMS`,新发现形态请追加、勿另写脚本)
- ✅ 误报已固化进工具:`--collisions` 模式会读 `shared_artifact_role` 并自动标注「有意共享(非缺陷)」,防止重犯 CAND-15
- ✅ 迁移映射表可一键生成:`--migration`
- ⬜ **未执行**。等 A1 全链跑完 → FIND4 阶段 → A/B 验证 → 才动库。
