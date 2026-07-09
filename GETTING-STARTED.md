# 团队第一天上手指南 · 用一个功能走完整条链

目标:**花半天,用一个小功能,亲手把 A→D 四条路径走一遍,学会整套 skill 怎么串起来用、以及"草稿要人审+测试"这条纪律为什么不能省。**

走完这一遍,你就能把同样的循环复制到你真实项目里的每个功能。

**前置**:装好 Claude Code,并 clone 仓库(见 [README 第 2 节](README.md))。

**我们要做的功能**(通用示例,和你的业务无关,照着走就行):
> 用户从钱包余额发起一笔提现。

选这个功能是因为它麻雀虽小五脏俱全——有状态流转(申请→审核→打款)、有权限(谁能审)、有并发和幂等(不能重复提现、不能并发把余额扣成负数)。这些正是 skill 最能帮上忙、也最容易出 bug 的地方。

---

## Step 0 · 把这条链要用的 skill 装好(2 分钟)

解压这几个 zip 到项目的 `.claude/skills/`:

```bash
mkdir -p .claude/skills
for z in \
  "完稿/N090 PRD产出与评审/022-prd-generation.zip" \
  "完稿/N150 API设计与校验/043-api-design-recommendation.zip" \
  "完稿/N160 数据模型设计/046-table-schema-design-recommendation.zip" \
  "完稿/N170 高级与非功能设计/049-concurrency-control-recommendation.zip" \
  "完稿/N170 高级与非功能设计/050-idempotency-design-recommendation.zip" \
  "完稿/N180 研发任务规划/055-development-task-breakdown.zip" \
  "完稿/N190 代码骨架生成/060-service-draft-generation.zip" \
  "完稿/N210 代码质量静态检查/073-transaction-boundary-check.zip" \
  "完稿/N210 代码质量静态检查/074-thread-safety-risk-check.zip" \
  "完稿/N260 质量门禁与专项测试/098-idempotency-test-point-generation.zip" \
  "完稿/N260 质量门禁与专项测试/097-concurrency-test-point-generation.zip" \
  "完稿/N220 Code Review与提交协同/078-pull-request-description-generation.zip" ; do
  unzip -o "$z" -d .claude/skills/
done
```

装完在 Claude Code 里就能直接用了——你正常说需求,Claude 会自动挑对应的 skill。

---

## Step 1 · 路径 A:一句话想法 → 迷你 PRD

**你做**:在 Claude Code 里,把想法 + 你已知的约束丢给它:

> 帮我为「用户从钱包余额发起提现」生成一份 PRD。已知约束:单笔最低 1 元、最高 5 万;每天最多提现 3 次;提现要走审核;审核通过后打款。

`prd-generation` 会产出一份带 16 节结构的 PRD 草稿(角色、状态流转、权限、数据对象、边界、待确认项)。

**你审**(这一步最关键,别跳):
- 状态流转全不全?(申请中 / 审核中 / 已打款 / 已驳回 / 打款失败——"打款失败"容易被漏)
- 边界和异常写清了没?(余额不足、超日限、并发重复提交)
- **它列出的「待确认项」你逐条拍板**——这些是它拿不准、需要你这个懂业务的人补的。输入越清楚,后面产出越好。

> 记住:PRD 的质量,直接决定后面所有产出的上限。这一步多花时间,是划算的。

---

## Step 2 · 路径 B:PRD → 技术设计

拿上一步的 PRD,依次让这几个 skill 出设计草稿:

1. **API 设计** —— `api-design-recommendation`
   > 根据这份 PRD,给提现功能设计 REST API。
   产出:发起提现、查提现状态、审核提现等接口的路径、入参、出参、错误码。

2. **表结构** —— `table-schema-design-recommendation`
   > 设计提现功能的数据库表。
   产出:`withdrawal` 表结构、字段、索引建议。

3. **并发控制 + 幂等**(这个功能的命门)—— `concurrency-control-recommendation` + `idempotency-design-recommendation`
   > 提现涉及扣余额,帮我设计并发控制和幂等方案,防止重复提现和并发扣成负数。
   产出:该用什么锁 / 版本号、幂等键怎么设计、请求重放怎么防。

**你审**:
- 幂等键是什么?(比如客户端生成的 `requestId`,同一个 key 只允许成功一次)
- 扣余额用什么并发策略?(`SELECT ... FOR UPDATE` 悲观锁,还是乐观锁 + 版本号)——**这一条一定要人来确认**,是最容易出资损 bug 的地方。

---

## Step 3 · 路径 C:设计 → 开发任务

> 根据上面的方案,把提现功能拆成开发任务。

`development-task-breakdown` 产出:任务清单 + 每个任务的依赖顺序 + 粗估工时。

**你审**:任务粒度合不合适、依赖顺序对不对、有没有漏掉"打款失败回滚"这类容易忘的任务。

---

## Step 4 · 路径 D:写代码 → 能提 PR(重头戏,纪律在这里教)

### 4.1 生成 Service 草稿
> 根据方案,生成提现的 Service 层代码草稿(WithdrawService)。

`service-draft-generation` 给你一份 `WithdrawService` 的实现草稿。

### 4.2 别急着用——先让静态检查过一遍
> 检查这段代码的事务边界和线程安全。

`transaction-boundary-check` + `thread-safety-risk-check` 会揪出草稿里的问题——比如"扣余额和写提现记录不在同一个事务里""并发下没锁,两笔请求能同时读到旧余额"。

### 4.3 生成必须过的测试点
> 给提现功能生成幂等和并发的测试点。

`idempotency-test-point-generation` + `concurrency-test-point-generation` 给你一组测试点,比如:
- 同一个 `requestId` 发两次,只能成功一次;
- 两笔提现并发打过来,余额不能被扣成负数;
- 余额刚好等于提现额时的边界。

**把这些测试写出来、跑起来。**

### 4.4 这就是全文最重要的一课
你会发现:**4.1 生成的草稿"看着对",但 4.2 的检查和 4.3 的测试,揪出了它漏掉的重复提现 / 并发扣款漏洞。**

这不是 skill 不好——是任何生成的代码都必须经过这一关。所以规矩永远是:

> **skill 出稿 → 人审工程判断 → 测试确认 → 才算数。**

省掉这一步,资损 bug 就会上线。这一条,是这份指南想让你记住的唯一一件事。

### 4.5 提 PR
> 帮我根据这次改动生成 PR 描述。

`pull-request-description-generation` 生成规范的 PR 描述(改了什么、为什么、怎么测的、风险点)。人过一遍,提交。

---

## 你已经走完了

一个功能,从想法一路到能提 PR,你用了大约 12 个 skill、走完了 A→D 四条路径。

真实项目里就这么干:**一次一个功能切片,重复这个循环。** 别整包生成、别跳过人审和测试。

---

## 一页纸 · 每步交付前的人审清单

| 路径 | skill 出什么 | 你过 PR 前必须确认 |
|---|---|---|
| A 想法→PRD | PRD 草稿 | 状态流转全不全、异常路径有没有、"待确认项"逐条拍板 |
| B PRD→设计 | API / 表 / 并发幂等方案 | 幂等键是什么、扣余额用什么锁——资损点人来定 |
| C 设计→任务 | 任务清单 | 粒度、依赖顺序、有没有漏回滚类任务 |
| D 代码→PR | 代码草稿 + 测试点 | **静态检查过了吗、并发/幂等测试写了并跑绿了吗** |

> 一句话总纲:skill 帮你把从零到八十分的时间省掉;最后那二十分的正确性,靠你的人审 + 测试兜底。
