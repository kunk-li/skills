# Status · Skill Platform

> **现状快照(覆盖式,不是日志)。** 规则:做完即从这里删 / 挪进当日 `_sessions/`,本文件永远 ≤ 一屏(~60 行)。想知道「现在」看这里;想回溯「当时」翻 `_sessions/`(逐会话流水)+ `_archive/`(重构前全量)。结构定于 D-042(2026-06-25)。
>
> 最后更新:2026-07-03 · 行数预算 ≤60

## 现在做什么(单一最高杠杆下一步)

**主线转向 = 开 N=1 完整闭环,直攻北极星头号缺口(至今 0 次干净 idea→prod)。** 用户 07-03 拍板:停在饱和的 skill-质量轴上排方向2/3/4(D-048 证边际回报零到负),转**单兵自起一个真内部小工具、全程走 skill 链**。方向1 已折入库封存(D-055,见 07-02 session)。

- **题面 = `skillctl`**:本项目 skill 库打包/校验/覆盖 CLI。选它因全是实痛(本机无 `zip`、D-055 重打包差点丢文件靠肉眼核、CHANGELOG bump 靠记、库恒 157 靠眼、CSV 154≠库157、19/157 覆盖无机器记录)。MVP=**pack + lint + count + coverage**(用户选最富版)。**已搬入本仓 `_tools/skillctl/`(随主项目版本控制、catalog 自定位仓根),已提交。**
- **今天 07-03 全链跑完 Path A→B→实现,MVP 功能完整、4 命令全在真库验过**:
  - 全在 `_tools/skillctl/`:Path A → `01-prd/PRD-skillctl.md`(N090/022 的 16 节 n090.prd.v2)。Path B → `02-tech-solution/SOLUTION-skillctl.md`(N130/039 exact-contract)。代码 `src/skillctl/`(pkglib/catalog/cmd_pack/lint/count/coverage/__main__),测试 `tests/`(18 断言全绿)。运行:`cd _tools/skillctl/src && python -m skillctl <cmd>`。
  - **闭环兑现的真价值**:① AC-1 正反例过——重打真 041 = 19 文件条目守恒+testzip OK;删 checklist.md 则精确报「丢失1条」+退码1+删半成品,**D-055 那类打包丢文件被自动拦死**。② count 名字级 diff 揪出真数据问题(4 个 zip 顶层目录带数字前缀、CSV 不带;`state-machine-driven-orchestration` 错配)。③ coverage=19/157=12.1% 且**全 19 个挤在 B 桶(prd→技术方案 036-054),A/C/D/E 全 0**。
  - **demand-pull 头号兑现**:PRD 里我推荐的 reinforced 判据(`### Evidence` 段)被**全库实测当场证伪**(只命中 1/19);真信号 = 含 CHANGELOG.md(恰 19/157)。真数据在我照错假设建实现前把它揪出——这就是 idea→prod 闭环的价值,非空磨 skill。
- **"优化 skills" = demand-pull 而非空磨(同 07-03 续)**:拿真 skillctl 代码捶 Path D(0/36)两遍。① code review 揪出并修了工具真 bug(count 名字没剥 `^\d+-`→把命名差异虚报成缺口;修后 157vs154 谜团解清=总表 CSV 4 处过时,已挂后台 task_2d0ede99)。② dogfood N230/080 补全 lint/count/coverage 测试=16 断言全绿,skillctl **MVP+测试完整、真可天天用**。**skill 信号(诚实):Path D 虽 0 强化但不弱**——N230/080 三分法首用即扛,两遍无系统性缺口,唯一候选 n=1 且不在其职责内。**本 session 零折(无真 PRE<POST delta),库恒 157。校准=别假设"0 强化=该补"(D-048 复现)。**
- **真用起来(用户选 a)= prod 端完整闭合**:`lint --all`(真用才暴露 lint 无全库模式的缺口→已加)全库体检 = 153/157 干净 + 4 warn;4 个非干净(143-146 顶层目录带数字前缀,lint+count 交叉证)用 `skillctl pack` 两阶段安全归一(暂存校验全过才落盘),现 **`lint --all` 157/157 干净、0 error**。git 恰好 4 zip 变、库恒 157、测试全绿。**skillctl 4 命令全在真库真用过、发现问题+解决问题一条龙**——北极星"0 次干净 idea→prod"第一条真闭上。
- **下一步**:① 续压 skill 优化换 A/C/E 段真工件捶(或同段多跑攒系统性再判折,D-048)② CSV 侧对齐 task_2d0ede99 ③ skillctl 可选:normalize 做成子命令、bump 内容 diff(FT-07)。

## 在途线程(每条一行:现状 + 下一步 + 细节链接)

- **OA G2 watch(只读 verify-only)· 07-01 纠错:G2 早已实质闭环,我这 session 把 STATUS 退回成「推不动」= 跟自己记忆 [[oa-live-n2-candidate]] 自相矛盾(它 06-17/06-22 已记「累计 3 条 master 干净 G2」)。** 双错根因:盯裸 `master` 指针没动、却没 grep 它内容里的 bug 号(gate④);且没信自己记忆。07-01 live 重验:**已在发布 master(03a891375 祖先)的干净 G2 = #2946(H6 USDT 尾签并发,`10597494a`)+ #2947(C2 双签防同人塌缩,`d015d6a62`,commit 显式「外部审计」)+ #2949(S1/P1 匿名命中 authz/boundary·HMAC 虚设,`39a9969fb`),全引用禅道号=我审计→禅道 bug→修并发版的完整链**。**在途**:#2972-2978(模块 03 认证 7 条)还在 `feature/master-0625`(领先 master 309 commits、07-01 还在推)未并 master;#2948(离职 TOTP 复活)仍开放。OA = 活跃 7+ 人天天发版真团队,但采纳只在**检测/审计片**(切片 G2,非完整 idea→prod 闭环,见「现在做什么」)。下一步 = 核 #2948 + #2972-2978 落 master 进度。
- **skill recall 棘轮(D-041)· ✅续9/10/11 全收口**:跨技能泛化跑完。045 R10 = fold_lifted(held-out 17.6→35.3%);048 R08 = fold_lifted(0→16.7%、NEW-vs-空基线、漏训练正例=未饱和);两者 cry-wolf 全 0。结论=棘轮能迁移、不掉精度、但增益小未饱和、n=1。**这条线判定可收**,不再炼新技能。细节 → DECISIONS ✅续9/10/11 + `generalize-045-R10-REFOCUS-2026-06-30.md` / `generalize-048-R08-2026-06-30.md`。
- **度量法学习(可复用)**:棘轮复验在大平表上,G+ 与两臂必须共享同一**语义有界区域**(R10=拒绝原因族 / R08=概念类×工件),否则 recall 测不出(✅续9 双 0 的根因)。

## 卡点 / Blocker

- **真缺口 = 无一次干净的 idea→prod 完整闭环**(切片信号已足:OA 检测片 + dream_true 下游 + CinemaAI 上游;头号场景 0 个)。公司无现成外部业务方(CLAUDE.md)= 完整闭环从哪来是开放题。候选:①自起真内部小工具单兵全程(最纯、零红线摩擦)②借 OA 真 PRD 跑 Path B/C 交团队(受只读红线)。
- head-to-head/干跑验证已收:证工具在设计评审/act-on-risk 轴达强基线(D-048),不再磨 skill。局限=纯静态、合成 seed、单 slice——要强结论仍需真 idea→prod 端到端。

## 按需细读(只给指针,不在此复制内容)

- 最硬测试 shortfall→4 方向(D-051)→ `D:/projects/skills-pilot/oa-pilot/oa-h2h-auth/SHORTFALL-to-skill-directions-2026-07-02.md`;标尺 `.../GROUND-TRUTH-normalpath-slice-2026-07-02.md`
- 方向1 A/B(D-052/053/054)→ 预登记 `.../oa-h2h-auth/DIR1-preregister-2026-07-02.md` · 第一对 `.../DIR1-RESULT-delta-2026-07-02.md` · n=2 `.../DIR1-VARIANCE-2026-07-02.md` · **n=5 终 `.../DIR1-VARIANCE-n5-2026-07-02.md`** · 产出 `.../tool-run-2026-07-02{,-POST,-PRE2..5,-POST2..5}/OUTPUT/`
- 两缺口折入决策包(逐条草案+审计+闭环计划)→ `D:/projects/skills-pilot/oa-pilot/headtohead-bug1334/FOLD-DECISION-actonrisk-gaps-2026-07-01.md`
- 战略 / 红线 / 工作风格 / ritual → `CLAUDE.md`(固定入口,SessionStart hook 已注入)
- 长期规划 + Phase 1 判据 G1-G5 + 当前阶段 → `ROADMAP.md`
- 已锁决策 D-001..D-042 → `DECISIONS.md`(冲突时按 D-号查,别重新决策)
- 逐会话历史 → `_sessions/`(最新一份 hook 已注入)
- 重构前 STATUS 全量 → `_archive/STATUS-pre-restructure-2026-06-25.md`;旧 changelog → `_archive/STATUS-changelog-2026H1.md`
