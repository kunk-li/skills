# Status · Skill Platform

> 这份文件**会经常更新**。每次 session 末尾必须 review 是否还准确。

**最后更新**:2026-06-05(**06-05 #3**:039 加选栈/语言 discipline〔业务 fit=038 C1-C5 + 团队擅长=038 C6,治 PRD 字面栈 vs 团队真实栈〕;**#2**:093 加 `reverse_coverage`〔code→spec 反向覆盖,治 PRD 滞后 shipped code,= 025 镜像,auth dogfood 已实证〕;**#1**:093 folded auth 镜头精化 = `mechanism-substituted` + `code-hygiene-drift` 2 verdict,先 verify 无硬编码枚举只改 SKILL.md,库 157;**#11**:025 完整性门禁加 provenance + 全 CRUD 推导〔Signal #6 落地,先 verify 确认 2/3 轴已存在只补真缺口〕,读回校验净、库 157;**#10**:hub-oa auth 模块 dogfood,032 AH-→093 验真 Java〔3 pass/1 换HOW/2 待核+2 drift〕,凑 roster+auth 2 模块样本;**#9**:28 改动 zip + 3 doc 沉淀进 git,先机械核验〔8 内容编辑 + 24 validator 补丁读回全在〕,库 157 不变;**06-04**:起 RepoProbe 服务 + 真外部 repo dogfood→detector 三修(嵌套入口/UTF-16/LLM-env)+ 干净全链 SDLC 重跑 5/9,详见顶部 🆕 块 + `_sessions/2026-06-04-session-1`。以下为历史)(session #1〔承接 06-01 #3〕· 后段新增 Signal #6 无原型→功能不全 + 转 OA 真项目验证 · 主体:**fork 拍 B** = spec↔现实验证层,两 skill 全建成;**重大结果**:用户指出 `video_ai` = CinemaAI 真实全栈实现 → 门禁 `code-static` 跑真代码 = **verdict `no_go`**(团队复核后 **4 真红线 + 1 撤回**:失败不退款/成功不落库/前端不拦/不对账;预扣竞态超扣经复核**撤回**——autobegin 使锁成立)。**Docker 非必需**。门禁价值实证 + 坐实 Signal #5 + D-003;**复核抓出我 1 条 concurrency overclaim = 健康的 verify 闭环**;后续:G2 首轮闭环=合格正信号(D-018)→固化进 skill v1.1.0;**D-019 用户拍板不增 skill→选 A:re-home 2 新 skill 进 032/093 ✅ 完成——032 加 AH-(v1.1.0)、093 加 built_vs_spec 维度、删 2 独立文件夹、净增 0、无重复;**06-03 续 · 新需求 = 全链路执行验证(UI→后端→DB→响应→UI 逐功能);用户倾向"自动测试代码"法(= G2 沉淀层,video_ai 14 测试已证)→ 折进 N230 `080`/N240 `086`+`088`,静态 `093` trace 退为覆盖缺口前置;已落「链路法」(N300 `trace-call-chain-analysis` 加 `chain_completeness_verify` mode,净增 0,验证 3 命中,记录 `_exec/2026-06-03-trace-chain-verify-mode.md`);「日志法」(`log-analysis` 加同名 mode 亦落,净增 0)/「测试法」(N240 `086` 加 `full_chain_integration` mode 亦落,净增 0)→ **全链验证闭环(四法 静态093/链路113/日志112/测试086 + 088 编排 playbook 串起;含 032 AH- 共 6 现有 skill 优化,D-018 发现器模型;**dogfood 验 hub-oa**(静态 stage 3 功能 3/3 结构 complete + 1 stub,工具校准:video_ai 报断/hub-oa 报通,报告 `skill-fork-b/hub-oa-fullchain-verify-dogfood.md;**链路验证 pack 已交付**:`skills-pilot/fullchain-verify-pack/`〔6 skill + plugin.json + 使用方法.md,可装〕`),净增 0)**(链路 113/日志 112/测试 086/静态 093,全优化现有、库始终 157),见 `_sessions/2026-06-03-session-1.md`**)** · **06-03 #2 续 · SDLC 测试阶段 dogfood(回到本体 Pilot)**:用户指回"用项目验证整个 skills"= Pilot 1 SDLC dogfood(D-004-OVERRIDE,前几 session 被 fork-B 占着没动)。把 N230 测试设计(080/082/083)应用到 RepoProbe 5 模块 → 产**真 pytest 套件 40 测试全 pass**(`skills-pilot/工作产物/05-test-stage-dogfood.md` + `skills-pilot/tests/`,Docker-free)。**3 skill 验强**(080/082/083 target-agnostic,无 API 的纯库代码也产好测试点,其 v2 universal-first 兑现)· **🔥 新信号 #7 = 库/CLI/SDK 类目无"可执行单测生成"skill**(N240 唯一产可跑测试码的 086 绑死 OpenAPI/HTTP;非 web 目标设计层强、代码生成层掉覆盖,同 infra #2/#3 族;**只记不建,守 D-019**)。**续 · N250 缺陷管理 dogfood**:把 05 挖到的 3 真缺陷(DEF-1 Flask `methods=POST` 被报 GET〔xfail 坐实〕/ DEF-2 客户端调用误判路由 / DEF-3 manage.py→cli 漏发现)喂 089→092 → 产可交工程缺陷包(`工作产物/06-n250-defect-mgmt-dogfood.md`)。**090/091/092 验强**;**🔴 089 抓到真内部矛盾**:示例用 `C2_product_code_bug` 但权威 taxonomy 定 C2=flaky test(stale 示例)+ C1-C6 缺"潜伏产品缺陷"槽(归因偏 CI-失败驱动)。**元 pattern 巩固:多个测试/缺陷类 skill 隐性预设「web+已上线+CI 驱动」形态,换形态(库/CLI/pre-ship/静态发现)掉槽**。**续 · ✅ 修 089(用户选①)**:`C2_product_code_bug`→`C1_real_regression`(9×)+ `C3_environment_infrastructure`→`C2_flaky_test`(4×)+ 归因C2→C1,共 **14 处标签纠正→canonical**;re-zip 回库、读回 zip **0 残留**、taxonomy 权威行+frontmatter 未动、git 可回滚。**= Pilot 首个「真用→暴露弱 skill→修好」闭环(find→fix→verify)**。附挖 `validate_skill.py` 无 `encoding=utf-8`→Windows GBK 必崩(疑库级共用脚本,候选修)。**续 · N270 发布就绪 dogfood**:6 skill 应用 RepoProbe → 诚实 readiness **RED**(门禁正确说"没就绪 + 缺口",没盖章 = 通过测试点)。**101/105 可用带形态债**(角色/12 维偏部署 web 服务,漏"执行不可信代码"命门维)· **104 canary 全 N/A**(无流量)· **103 rollback 退化**(CLI=revert pip/git)· 100/102 适用。Signal #7 **第 3 节点族加固** + **validator-utf8 勘明并纠错**(⚠️ 我先 overclaim「N270 `validate_artifact.py` 同 bug」→ **全库扫描证伪**:它有 `encoding="utf-8"` 没事;**真 bug = `validate_skill.py`,24 个 zip〔技能 076-099,N220-N260 测试/门禁块〕,2 变体,一行 `encoding="utf-8"` 可修**。根因 = `grep|head && echo` 中 head 总 exit 0 掩盖 grep no-match → 又一次"分析跑在验证前")。**✅ 已批量修 24 zip + 验证**(24/24 patched+verified、全库 0 残留、两变体 validator 实跑 `1/1 passed`、089 标签+validator 双修共存、git 27 zip M 可回滚)。`工作产物/07`。**续 · N300 运行/故障 dogfood**:RepoProbe 真跑 5 配置产真运行日志 → 套 N300 9 技能。**112/114/116/117 分析类可用**(112 还抓到 RepoProbe 真 gap = 捕获被测 repo 输出**无脱敏**→漏密钥风险)· **111/113/115/118/119 遥测类 N/A**(无指标/trace/告警/用户影响)。**Signal #7 第 4 节点族 = pattern 饱和**(分析层通用 / 采集遥测层绑已部署 web 服务)。次:RepoProbe 自身 5 路径行为正确(二次验)。`工作产物/08`。**⚠️ 连 4 阶段磨刀,Signal #7 边际洞递减 → 建议收尾(汇总优化清单)或转 G2(连 4 次提醒未答)。** 库不变(157),见 `_sessions/2026-06-03-session-2.md`

---

## 🎯 当前状态 + 下次接这里 ← LOOK HERE FIRST

> **🆕 2026-06-05 #3 · 039 加"选栈/语言 = 业务 fit + 团队擅长"discipline ← 最新先读这条**:用户洞 = 架构/语言该按 PRD 业务场景 + 使用人员 + **团队擅长领域**定,非 PRD 字面。**先 verify**:038 technical-solution-analysis **已有** 6 约束维 C1-C6,`C6_human_resource`=team size/skills/hiring(团队擅长已建模);但 039 technical-solution-draft-generation(真出架构 S3 + 推荐 S1 那个)**零** stack/语言/团队字样 → **C6 被收集、没流进选栈**。正是 hub-oa 谜题机制(栈推荐悬空于团队 → PRD NestJS / 团队 Java)。**修(D-019/D-023)**:039 加 `### 4b technology stack and implementation-language discipline`——选栈/语言须**显式决策** + 双轴 justify(业务 fit=038 C1-C5 / 团队 capability=038 C6)+ 列 rejected stacks & why(「团队不熟 X」= 合法否决)+ C6 未知时标 `to_confirm` 不硬塞 + 1 条 self-check。读回校验:5 markers / 零项目字样 / zip 17-17 只动 SKILL.md / testzip ok。库 157。**= verify-before-claim 又省一次重复造**(团队约束 038 早有,只补 039 wiring)。**未提交(本 session 累积)**:093 reverse_coverage + 039 + STATUS + session。
>
> **🆕 2026-06-05 #2 · 093 加 reverse_coverage(code→spec 反向覆盖,治"PRD 滞后 shipped code")**:用户选 A → 给 `093 built_vs_spec` 加**第二方向**。默认 spec→reality(`032` AH- 核代码)对"实现领先 spec"**全盲**(没 AH- 就不查),而真实/成熟项目**反向漂移是主向**。`reverse_coverage`:从实现侧枚举**契约级/可观测**行为(端点/状态迁移/定时任务/钱·权限·数据·审计副作用)与 spec AH- 求差 → 浮现「代码有、spec 无」块 = **spec backfill 候选**。防误报:只对契约级求差、不扫 helper/胶水;**发现器非门禁(D-018)**:一律 `provisional`、绝不驱 `no_go`、人裁分流(回写 PRD / 保留 / 砍影子功能)。= **025 complete-feature(spec 侧)的镜像**,两侧夹逼 spec↔code 完整性。**已被 auth dogfood 实证**:org 改/归档 + 用户复活(代码有 PRD 无)正是 reverse_coverage finding(025 demo 已抓到,本次把这一类**形式化进 093**)。读回校验:5 markers / 零项目字样 / zip 23-23 只动 SKILL.md / testzip ok。库 157。**未提交**:093 zip + STATUS + session。
>
> **🆕 2026-06-05 #1 · 093 折入 auth dogfood 2 条镜头精化(D-022 杠杆)**:把 06-04 auth dogfood 挖出的 2 条方法论反哺进 `093` 的 `built_vs_spec` 维度(优化现有 / 通用,守 D-019/D-023)。① **`mechanism-substituted` verdict**:架构换 HOW(实现用 ≠ spec 的机制满足同一断言)别 blanket-N/A,要从 `AH-` 抽底层意图(WHAT/红线)核新机制是否仍满足——全满足 pass、部分列精确残留 partial、完全不满足才 fail。② **`code-hygiene-drift` verdict**:行为对但用了废弃/被取代/自相矛盾的内部契约(抛 deprecated 错误码、调已移除路径、用冲突标签)→ 行为 pass + 单发 finding 交人裁,不阻断,技术债发现器(doc-vs-doc + 合成 eval 抓不到)。**先 verify**:扫 093 全 zip 确认**无 reference/validator 硬编码 built_vs_spec verdict 枚举**(`spec-stale` 只在 SKILL.md 出现 1 次,validator 只查 `verdict` 字段存在性 + gate 级 `status` 枚举,两回事)→ 只改 SKILL.md 安全一致。**读回校验**:2 verdict + 子规则全在 / 我的新增零项目字样 / zip 23-23 条目只动 SKILL.md / testzip ok。库仍 157。**✅ 副带清理(builder 拍板 genericize)**:这段 built_vs_spec 原有 **2 处 pre-existing `video_ai`**(D-018 实测例)= D-023 smell → 已 genericize 为「某真实全栈项目」/「某真实项目」,例子价值(3 红线 / 14 PG 测 / 2 lint)保留,**全 SKILL.md 现零项目字样**(grep 验)。
>
> **🆕 2026-06-04 #11 · 025 完整性门禁加 provenance + 全 CRUD 生命周期推导(Signal #6 修法落地)**:用户洞 =「PRD 不可能穷举后端功能 → 中间产物需『功能→伴生需求自动推导』:新增→验删除/修改、原始数据来源/创建方式、异常链路」= STATUS 早记的 **Signal #6**。**先 verify(守 Signal #6 备注『先验 025 查什么』)**:读真 025 SKILL.md → **2/3 轴已存在**(`create implies delete`+symmetry create/delete = CRUD 删除;`success implies failure`+`external dep implies fallback`+D5 = 异常链路)→ **没重复造已有能力**。**真缺口 = 数据来源 provenance(关键词全 0 命中)+ 修改/全 CRUD(原仅 create→delete)**;013 是纯结构化不推导 → 推导归 025。**修(D-019 优化现有 / D-023 通用零项目字样)**:Implicit rules +4 条(full lifecycle siblings read/update/delete · data consumption implies provenance · reference implies creation path · derived implies source dataset)+ 新 `## Provenance check` 小节 + `provenance_gap` finding 类型 + workflow step3。**续 · 用户给出『完整功能』4 支柱定义(原始信息来源 / 完整实现链路 / 完善操作过程 / 异常处理机制)→ 编码成 025 的 `## Complete-feature model`**(per-feature 核 4 支柱 + `feature_completeness` finding,映射 D2/D8/D1/D5;支柱②实现链路 = spec 侧在 025、运行时在 093/113 → **该模型统一了 Signal #5〔链路〕+ Signal #6〔完整性〕**)。**两次编辑均读回校验**:markers 全在 / 零项目字样 / zip 17-17 条目保全只动 SKILL.md / testzip ok / .bak 已删+gitignore。**= 真用洞→定位通用类→精准优化现有 skill 闭环,且 verify 拦住『重复造 025 已有的 CRUD+异常推导』**。库仍 157。**demo 已跑**(`skill-fork-b/hub-oa-auth-025-complete-feature-demo.md`):auth 821 行真 PRD 上 4 支柱核 4 功能 → **2 真 gap + 1 minor**,2 gap 经真 Java file:line 证实「PRD 漏、代码有」(组织改/归档 `SysOrgServiceImpl.edit:125`+`SysOrgMapper:52`;用户复活 `OaReactivationController:43`)= **Signal #6 实锤**;TG 登录判 complete(4/4)= **不逢扫必报**(校准力)。**未做**:把 auth 轮 093 镜头精化〔换HOW核WHAT + code-hygiene-drift〕折进 093;commit 本轮全部。
>
> **🆕 2026-06-04 #10 · hub-oa auth 模块 dogfood(2 模块样本 roster+auth)**:用户选 A(正向保真)→ `032 AH- → 093 built-vs-spec` 用到真实 hub-oa auth(Java `hub-plugin-auth`)。读 821 行 auth PRD 派生 **6 条栈无关行为红线** → 亲核真 Java + file:line → **3 pass(2 超出)/ 1 not-as-specced(换 HOW)/ 2 待核 + 2 drift**。产物 `skill-fork-b/hub-oa-auth-behavior-fidelity-093.md`。**3 条新收获**:① 新 finding 类型 **code-hygiene drift**(`AuthServiceImpl:2302` 仍抛 ADR-075〔2026-05-26〕已废弃的 `RBAC_L1_WEB_BLOCKED`,应迁 `PC_ACCESS_DENIED` 未迁;行为对、契约旧——doc-vs-doc 永抓不到)② **镜头精化**:架构换 HOW(cookie→sa-token)≠ 无脑 N/A,要核「新 HOW 是否仍守原 WHAT」(AH-A05:CSRF 满足、XSS-token 存储待核)③ **Signal #5 反向漂移在 auth 比 roster 更剧烈**:PRD=Phase-1/8 角色 L1-L4/NestJS,实现=L6+Z/Y/J 多序列+TOTP/双L6+区域+法务孤岛+副职令牌 → **PRD 角色模型整体被实现取代**。**镜头复证**(2 模块一致):PRD↔代码验证 = 验行为红线(WHAT)不验架构(HOW);成熟项目实现几乎总领先 PRD,真缺口在 PRD 没写全的长尾(Signal #6)。**093=发现器非橡皮章**(3 flag 机械抓出交人裁,没硬判)。⚠️ 诚实:auth 单模块 6 红线样本非全量;Path C 代码生成 + 086 运行时「对不对」仍需团队真栈。
>
> **🆕 2026-06-04 #9 · dogfood 改进沉淀 + 机械核验 + commit(用户选「先沉淀」)**:把累积未提交的 dogfood skill 改进**封存进 git**(此前 28 个改过的 zip + DECISIONS/ROADMAP/STATUS 一直 uncommitted)。**先机械核验再 commit**(守本项目"验证跑在断言前"的纪律,verify-before-claim):脚本读回每个 zip 核对 dogfood 编辑 —— **8 内容编辑全在**(032 `AH-`/054 `D5 untrusted-execution`/082 `BK11 portability`/086 `library_unit`/089 canonical 标签且 stale `C2_product_code_bug`/`C3_environment` 清零/093 `built_vs_spec`/112+113 `chain_completeness`)+ **24 个 validator `encoding="utf-8"` 补丁全在** + 28 zip 完整性 ok。⚠️ 核验中 054 一度误报(我 marker 用下划线 `untrusted_execution`,实际文本是连字符 `untrusted-execution` → 查源证实编辑真在 = 又一次 verify 拦住假阴性)。**库仍 157**(`N320-N360_skills.zip` 冗余 bundle 删除 = 那 20 skill 已拆成 5 个文件夹独立 git-tracked,非丢 skill)。加 `.gitignore` 排除 `hermes-agent/`(160M dogfood clone)+ `_rehome_work`/`_skilledit`(scratch)+ `.claude/.stop-counters`(churn)+ `launch.json`(指向已弃 Skills Studio)。**09 优化清单 P1/P2 未碰**(用户选先沉淀;清单原地待命,D-024 已拆 G2 闸 → 随时可执行)。commit 见 git log。
>
> **🆕 2026-06-04 #8 · 战略收窄(用户拍板 option 1 · D-026)**:用户真用 hermes-agent 真跑→🔴(查明 = compose `network_mode: host` 无端口映射 + API server 默认关 + 要密钥),并点破核心:**"真跑不了,工具就没意义"**。我没继续打补丁,给了诚实战略判断:**"自动真跑任意 repo"是固有难题**(重栈需密钥/权重/外部服务/特定网络,E2B/Modal/Devin 同样做不到),非可补 bug;再修 host-network/端口/超时 = 填不平的坑。**用户拍 option 1 → 收窄(D-026)**:真跑只保**自包含/有运行约定** repo(`_sample_web` 18.9s 绿),**重栈给 LLM 速览 + 诚实诊断,停止追真跑覆盖率**;web UI tagline 已改诚实(说清适用范围)。**定位锁定:RepoProbe = 已达成使命的 skill-dogfood 夹具(真实产出 = 打磨硬的 skills),不是通用真跑器 → 投入重心回 skills/北极星。** 另:本轮加了报告「📋 复制报告」按钮(grep 验过)。⚠️ 自评:我这几轮多次发坏工具调用(`count<invoke>` 乱码)= 我的执行失误,已纠。
>
> **🆕 2026-06-04 #7 · 静态/mock 加 LLM「1 分钟速览」(治"路由清单没意义")**:用户两次说 mock 输出(路由 inventory)没意义——对,reframe 是擦口红,根因 = mock 只正则抽路由 = 浅,用户要"看懂它"。修(RepoProbe 代码 + 复用已接 qwen):`llm.llm_summarize` 读 repo 关键文件 → 出『**这是什么 + 技术栈/怎么跑 + 接口按功能分组 + 值得注意**』1 屏速览(= 当初砍的 F017),`boot`→`report` 渲染在「能跑吗」下方;无 key 优雅回退;有速览时原始路由清单收成 8 条样本。**实测 hermes-agent**:qwen 正确判"自进化 AI 代理系统"+ 7 组接口 + 3 条带真实模块名的架构/风险点。**= 有限重开"解释"(D-025;理由 D-024 真用户要看懂;边界 = 1 屏速览非 wiki,差异化仍是'+能否真跑')**。⚠️ 已知:web server 单线程,一个请求(LLM 速览 10-60s / localdocker build 数分钟)期间对别的请求不响应(非崩,忙完即恢复)。⚠️ 后台 server 任务跨 session 残留孤儿壳(进程已死、面板手动 ✕);活服务=最新那个。
>
> **🆕 2026-06-04 #6 · config-indirected 端口检测(用户选 option 2)**:`detector._detect_port` 原只抓字面量(`.run(port=8000)`/`--port`/EXPOSE),抓不到**端口经配置对象引用**的 repo(如 OCR repo `settings.py: port=20000` + `uvicorn.run(port=Network.port)`)→ 退默认 8000 → 真 boot 探错端口。**通用修**:加 `_PORT_CONFIG` 正则(`port [:=] N`,前导收紧防 support/report/export 误判)+ `_decode` 编码稳健 + 扫 `.toml/.yaml/.env/.ini/.cfg`;**字面量优先、配置式兜底**。**+5 测试(65 pass,含防误判)**;实测 OCR repo 现报 **端口 20000**(原 8000)+ convention/嵌套入口。→ 把"端口写配置里的中量级 repo"推进真跑满值档。RepoProbe 代码修(非 skill)。server `bh2ke90rh`。
>
> **🆕 2026-06-04 #5 · 真用(builder=外部用户 D-024)撞 RepoProbe 两 UX/价值洞 → 修**:用户起服务真用,丢 `hermes-agent`(多服务 compose)。① **mock 输出"没意义"**:verdict 假报"能跑"(实则没跑)+ 361 路由全是重复样板"待 boot 真探" → 修 `report.py`:mock verdict 改 **🔵 静态分析(未真跑)**;surface 拆 probed/unprobed,unprobed 压成 **"静态发现 N 个接口面(API surface 清单)"** + 列 40 + "还有 N 个" + 一句引导(不再 N 行样板)。② **localdocker compose 300s 超时裸崩 + 泄漏半 build 栈** → 修 `sandbox.py`:`BUILD_TIMEOUT_S` 300→600 + **超时 catch + `down -v` 清理 + 可操作信息**。都是 **RepoProbe 工具修(非 skill,不涉通用性)**。验过:hermes mock 现报 🔵 静态分析 + "静态发现 361 接口面"。server `b7vm7hln4`。**诚实价值边界**:RepoProbe「自动跑起来看」对**轻/中 repo 满值**(`_sample_web` 18.9s 真跑🟢),**重 repo(ML/多服务/大 build)过实跑天花板** → 退化为"静态 API map + 诚实超时";两修让两档都不再无用。
>
> **🆕 2026-06-04 #4 · skill 通用化修复(082 加 BK11 跨环境边界)+ 全链重跑(完成)**:用户指令 = "修 skill 但**通用、别只针对 RepoProbe**" + 修完**重跑完整 SDLC 全链**。**Part 1 完成**:把真用挖出的"跨环境输入"洞(Windows 路径 + UTF-16 同族 = 输入来自与运行时不同的环境)**通用化**修进 **`082-boundary-condition-generation`**——加 `BK11_portability_boundary` 边界类(路径分隔符/盘符·UNC·POSIX/编码·BOM/CRLF·LF/locale/OS 来源↔执行错配)+ `R08_portability_boundary` 规则 + 路由行 + 算法步 + edge-catalog 的 cross-environment 清单 + BK01→BK11 同步。**全通用表述,零 RepoProbe 字样**。改 3 文件(taxonomy/SKILL/edge-catalog),re-zip 回库**验过**(BK11+R08+catalog 在、19 entries),原 zip 备份 `_skilledit/082-ORIG.zip.bak`。**库计数不变(优化现有,D-019)**。**Part 2 完成 = 用修复后 skills 重跑完整链**(`sdlc-run-2/01..08`,8 阶段:需求→PRD→原型→PRD-to-code→架构→代码→测试→部署,反映当前 RepoProbe 含路径修复+进度 UI)。**BK11 跨环境边界这次被链路接住**:F003 需求 → PRD§7 可移植性 → AH-P01/02/03(Stage 4 验收)→ **修复后 082 生成 BK11 用例(Stage 7)→ 60 测试含 7 可移植性 → 093 核 AH-P 全 pass**。**= find→fix→verify 在 skill 层闭合**(v1 整链含验证脊对这类 bug 全盲、靠真用兜底;v2 链路自接)。Stage 8 补跑 v1 跳过的 `107`,并坐实**跨环境输入归 BK11(082)非 107**(107 scope 是 staging↔prod parity)。
>
> **🆕 2026-06-04 #3 · 真用再暴露 Windows-路径 bug → 修 + 端到端实证**:用户经 **web UI** 用 **Windows 路径** `D:\projects\...` 喂 OCR repo → 垃圾结果(`llm` 瞎猜 server.py:8000 + build 失败),判"功能完全没实现"。**复现坐实**:web server 在 WSL,`D:\` WSL 看不到 → detector 落 heuristic → LLM 凭空猜(WSL 路径 `/mnt/d/...` 则正常 `convention/web/python -m src.api.app`)。**根因 = `fetch.resolve_repo` 没把 `D:\x`→`/mnt/d/x`** → 修(`fetch._to_local`,+7 测试,**60 pass**)。**次要发现**:legacy docker build 其实正常(实测 `Successfully built`,**不需 buildx**),报告把 stderr 弃用警告误当 build 错误(misleading,候选修)。**端到端实证**:重起 server,①OCR Windows 路径经 web 现 `convention/web`(路径修复生效)②`_sample_web` 真 localdocker **18.9s → 🟢 能跑 + `/health` HTTP 200 `{ok:true}`** = 核心真跑(非 Mock)。诚实:**OCR 全 boot 仍边缘**(ML 重依赖 PyMuPDF/tesseract + 端口 20000 config-indirected→探 8000 会 miss)。**教训:dogfood 一直用 WSL 路径 + CLI,漏了"Windows 用户经 web UI 输 Windows 路径"这条真实主路径 → 真用才暴露。** server 任务 = `bmne71g9f`。
>
> **🆕 2026-06-04 #2 · RepoProbe 干净全链 SDLC 重跑(9/9 完成)**:用户拍板 = 走 RepoProbe 自 dogfood(听过北极星「外部/G2 价值更高」后仍选它)→ 用**改进后 skills** 把 RepoProbe 最终 ship 形态从**立项跑到部署**,产一条连贯 canonical 工件链(demo 弹药)+ **逐交接显式追踪保真度(Signal #5 的 forcing function)**。已搭脚手架 + 9 阶段任务 + **全链 9/9 完成**:`skills-pilot/sdlc-clean-run/`(README 进度表+交接保真表 + `01-feasibility..09-release`)。**验证脊 `032 AH-→054 SEC→093 gate` 在真代码端到端闭合**:093 拿 12 条 AH- 机械核 `repoprobe/*.py` → **11 pass + 1 split(web egress critical residual,诚实 flag 不盖章)**;086 library_unit = 53 库测全绿。**4/4 改进 skill 在链里真长肉**(032 命门→4 AH-S / 054 D5→SEC-### / 086→53 库测 / 093→11/12 机械核)。**3 条 meta 发现**:① 漂移双向,**shipped 产品里「文档落后代码」是主向**(链中 3 次实现领先 spec → 真 ship 后须回写 spec,否则 demo 低估产品)② 验证脊端到端可机械追溯命门 + 诚实钉唯一 critical 残留 ③ 干净身份卡(Stage 1 锁「不做」)= scope 纪律源头(Signal #5 上游解)。**产物 = 给真实 Pilot 团队的 canonical demo 链 + 可量化改进-skill 价值证据。** **下一步偏战略**:G2(真人/外部用 skill,需社交动作我做不了)仍是更大未答题——现在有 demo 弹药了;次选 = config-port 检测 / web egress 锁定(v2,RepoProbe 余量)。
>
> **🆕 2026-06-04 · 真实外部 repo dogfood → detector 嵌套入口洞修复**:用户拿**真实外部 repo** `D:/projects/python/ai_work/document_recognition_system`(FastAPI OCR 服务,`src/api/` 分层 router + `examples/` 入口;**非玩具样本、非我自己的码 = D-004「builder 自证」盲区首次真外部输入**)喂 RepoProbe web UI → 报「⚪ unknown/heuristic 跑不了」。用户判「target 松散像脚本」——**核 app.py 证伪**:它是干净 FastAPI(lifespan+CORS+4 router+`uvicorn.run`),是 detector 的锅。**根因 3 处全 file:line 坐实**:① detector **只扫根目录**(`_has` `detector.py:22`、约定循环 `:123`)→ 嵌套 `src/api/app.py` 看不见 → heuristic ② requirements.txt 是 **UTF-16**,`_read_lower` utf-8 读 → `fastapi` 被空字节打散匹配不上 → kind 误判 unknown(**同 validator-utf8 编码假设族**) ③ LLM 兜底 **0.0s 没触发**:根因 = 启动命令 `VAR=val exec python3` 没把 `RP_LLM_ENV_FILE` 传进进程(exec 特殊 builtin)→ `_config`(`llm.py:90`)无 key 立即 return。**已修 ①②③**:①② 在 `repoprobe/detector.py`——加 `_find_nested_entry`(子目录找带可运行信号的入口 → `python -m src.api.app`)+ `_decode`(按 BOM 稳健解码 UTF-8/16);③ 启动命令改 `export`(WSL 块已更新)+ web server 已用新写法重起、environ 实测 `RP_LLM_ENV_FILE` 已设。**验证**:53 单测(+5,含嵌套入口/UTF-16/精度边界)无回归;target 重跑 mock → `method=convention` `kind=web` `python -m src.api.app` + **静态扒 33 路由**(之前 0)。**= Signal #5/#7 形态洞在真外部 repo 上的正面实证 + find→fix→verify 闭环(detect 层,非 target)**。**剩**:port 从 config 对象取(`Network.port=20000` 经变量引用,`_detect_port` 正则抓不到 → 报默认 8000;config-indirected 端口是已知短板)/ 真 localdocker 重 boot 未试(ML 重依赖 PyMuPDF/tesseract/paddleocr,likely 慢或缺系统依赖,届时 RepoProbe 会诚实报"启动到哪崩")。**web server 已用新 detector + export 重起,localhost:8900 可直接复测。**
>
> **🏁 2026-06-03 #2 session 结束态**:超长 session。**RepoProbe 已建成可用产品(v1+v2)** —— 本地+远程 repo、CLI + web UI(**live @ http://localhost:8900**,后台任务 bdqa6sue0)、约定/无约定(LLM-assist qwen)/多服务(compose)全支持;`tests/` 48 单测全过;打包好(`python3 -m repoprobe` + pyproject + 使用方法.md)。**两个北极星级结果**:① **G2 兑现**(D-021:video_ai 真团队真栈修资金红线 + 真 PG 测捡出 mock 测不到的新 prod bug)② **验证脊端到端实证**(D-022:RepoProbe 自己的真洞 → 032 `AH-`→093 `built-vs-spec`,3 个不知情盲核 agent 抓洞 + 抓出我半吊子修复 + 修全 PASS;`工作产物/12`)。**下一步偏战略(别再磨低价值 skill backlog)**:让设计 skill 可靠产完整 AH-(D-022 杠杆 = Signal #5/#6 正解)/ 找真外部用户用 skill 库(D-004 盲区:至今 builder 自证)/ RepoProbe 余量(egress 需防火墙授权、surface 非声明式路由 LLM 推断)。**机器**:WSL 原生 dockerd + RepoProbe server 在跑,重启命令见下「▶ WSL Docker」块(清残留 server 按 PID `kill -9` 别 pkill 自杀)。**全貌见 `_sessions/2026-06-03-session-2.md` 🏁 收尾段。**

> **🟢 G2 兑现(2026-06-03 · D-021)= "G2 仍待"那条的答案**:video_ai 团队把 built-vs-spec 审计的资金红线 + `对`-stage 真 PG 测**实施了**——修原子结算/失败退款/幂等 + **真 PG 测捡出新 prod bug**(create2 `task_type` 22 字符 > `VARCHAR(20)` 生产提交即 500,mock 永测不出)+ 结构护栏(`SETTLEMENT_WORKERS` 覆盖 4 worker,CI 防回归)。8 新集成 + 22 集成 + 234 单测 + 7 护栏全绿。= **真栈验证 > doc-vs-doc/mock 从断言变实证**;北极星首个真团队/真栈价值证据。⚠️ 本条来自**验证 arc(本对话分支)**,与下方 06-03 #2 RepoProbe 主线为两条并行线,**builder 已定(06-03):RepoProbe = 主线**;本验证 arc + 此 G2 收为已完成侧线(成果留档,不再投入)。

> **📨 侧线→主线 · 086 共编交接 ← #2 改 086 前必读**:验证 arc 已收口、**侧线即日不再动库**(库稳定 157)。**唯一冲突点 = 086**:侧线已折入并验通 `full_chain_integration` 的「真用补充」段(真 DB 抓列宽/约束/类型 bug + `SETTLEMENT_WORKERS` 护栏);你加 `library_unit` mode 前**必须从当前库 zip 重新 extract**(否则冲掉它),且**别用 `_rehome_work`**(两线共用会打架,改用独立目录 + 原子 extract→edit→`Compress-Archive -Force`)。库 6 处优化权威清单 + 自检锚点见根目录 **`HANDOFF-verification-arc-to-RepoProbe-2026-06-03.md`**。

> **🆕 06-03 #2 收口 ← 先读这条**:本 session 把"用 SDLC dogfood 验整库"走完 **4 阶段(N230/N250/N270/N300)**,净增 0、库始终 157;落 **2 个真修复**(089 示例标签 14× + validator-utf8 ×24 zip〔076-099〕)+ **1 次 overclaim 自纠**(全库扫描拦下)。**Signal #7 四族饱和** = 分析/推理层 skill 通用,生成-遥测-部署层绑"已部署 web 服务"形态(RepoProbe=反例)。收口产物:`skills-pilot/工作产物/09`(优化清单,**排在 G2 后**)+ `10`(G2 开箱即发包:E1 暖联系 video_ai / E2 新项目 Path A + 开场白)。
> **G2 社交动作**(按 `工作产物/10`,只有 builder 能做)仍是更强的价值证据。
> **🔀 06-03 #2 后半转向(D-020 用户拍板)← 当前主线**:RepoProbe 从"载体"**升格为要真 ship 的产品**,build 即并发优化 skill(= 北极星 N=1 形态,非偏离)。🎉 **解了 4 session 的 Docker 老结**:Desktop 的 WSL backend 被删 → 改在 **Ubuntu WSL 装原生 docker.io(`wsl -u root` 免密)**→ **首次真 boot 成功**(`_sample_repo` CLI 真 build+run,捕获真容器输出 `result = 42`,34.7s)→ **detector→sandbox→build→run→capture 全链首次真验证(非 Mock)= RepoProbe 大去风险**。**✅ step 2 完成:web 真 boot + 真行为探测**——`_sample_web`(Flask,convention)→ 合成 Dockerfile → 容器跑起、端口仅发布 `127.0.0.1:32768` → **真打 `/health` 得 `{ok:true,result:42}`(运行中 app 的真实产出)** + teardown 零泄漏。安全 v1 姿态(localhost 端口 + 资源限额 + no-new-privileges)生效;**残留命门 = 容器仍可出网,egress 锁定 = v2**。改了 `sandbox/surface/boot` + 1 测试,Windows 40+1 单测无回归。**= 产品核心命题「丢 repo → 自动跑起来 → 看真实产出」首次真证(非 Mock)。** ✅ **dogfood N170 `security-risk-analysis` 已做**(`工作产物/11`):STRIDE 框架在、有用——逼出 RepoProbe **5 条真加固**(pids-limit/cap-drop/非root/read-only/seccomp + egress + 脱敏);**但缺"执行不可信代码/sandbox"专门子域**(默认控制 MFA/SBOM/合规全 N/A,relevant 控制不在它 catalog,我自己硬套 STRIDE 出来的)→ **优化候选 = 054 加 `untrusted_execution` 威胁子域 + 控制库**(D-019,**从真建侧坐实 = Signal #7 第 5 证据**)。verify-before-claim 第 4 次起作用(没说死"054 不行")。**✅ 用户方向校准(关键)**:一路把 RepoProbe 建到完成,**skill 优化是副产物(边建边记)、不逐步征询**。本轮驱动 3 块:① sandbox 加固(`--pids-limit 256 + --cap-drop ALL + no-new-privileges`,测 CLI+web boot 不破)② **端口检测**(静态扫 `app.run(port=)` 等,`_sample_web`→8000,脱硬编码,`detector._detect_port`)③ **reporter**(`repoprobe/report.py` = 产品真输出"能跑吗/产出啥/哪崩")。**→ 核心环 `detect→boot→probe→report` 完整**:真跑 `_sample_web` 出干净报告(🟢 能跑 + `/health`=`{ok:true,result:42}`),Windows 40+1 单测无回归。**剩到"产品完成":真实外部 repo 验证(脱玩具样本)/ LLM-assist(无约定 repo 的 heuristic + 非 web surface 推断)/ compose 多服务(现单容器近似=fake)/ 打包 CLI。继续驱动,不再每步问。**
> **✅ 首个真实 repo 验证 + gap 修复闭环**:喂真 `skills-studio/api`(FastAPI+DB)→ RepoProbe 真 build+boot+探 23 路由(67s),`/api/v1/health`/`/config` 等真 200(app 真跑、连 DB)。**逼出真 gap**:surface 只抓装饰器路径、漏 `include_router(prefix=)` 挂载前缀 → 21 假 404。**已修**(probe 对 404 回退试 `/api/v1`/`/api`/`/v1` 前缀,`surface.py`)→ 重验:10+ 路由全 `@/api/v1` 命中真 200,剩 404 是带路径参 `{id}` 的真 404。40+1 单测无回归。**→ RepoProbe v1 核心功能完整 + 真实 app 验证通过**(detect→boot→probe→report,含带前缀真 app)。**✅ 打包完成**:`python3 -m repoprobe <repo> [--sandbox][--json]` 入口(`__main__.py` argparse + 退出码 0=能跑/1=不能,便于 CI)+ `pyproject.toml`(`pip install -e .`→`repoprobe` 命令,需先 `apt install python3-pip`,WSL 默认无)+ `repoprobe/使用方法.md`;模块入口已验通(报告+exit 0)。**= RepoProbe v1 完成**(detect→boot→probe→report + 真实 app 验证 + 安全加固 + 打包 + 40+1 单测)。**剩 = 纯 v2 扩展(LLM-assist 无约定 repo / compose 多服务 / egress 锁定)——v1 scope 已收口。**
> **✅ skill 优化回流相开始(v1 完成后 = 用户序;G2 已兑现 D-021 → 09 清单闸门开)**:① **054 `security-risk-analysis` 加 D5 `untrusted_execution` 威胁子域 + 控制库**(re-zip 回库验通:D5/trigger/desc/控制 catalog 全在,15 entries 结构完整;D-019 加子域非新建,库 157)。② **086 加 `library_unit` mode** ✅(消费 080 测试点 → 出函数级 pytest 骨架,治库/CLI 无可执行单测生成;re-zip 验通,与 full_chain_integration + validator-utf8 修复**共存**,21 entries,库 157)。**→ 2 个最 build-grounded 优化回流完成**(054 = 真建需求〔RepoProbe sandbox 命门〕/ 086 = 真建产物〔RepoProbe 40 个手写单测正是此形态〕)。**剩 09 清单(089 C7 槽 / 遥测 no_telemetry / N270 降级)= dogfood-survey 类、ROI 偏低,留 backlog 按需取**——别为补 gap 而补(v1 已完成,价值已由 G2 D-021 + 真建证)。
> **🚀 v2 推进(用户:继续推 v2)· LLM-assist 已落 + 验通**:compose 插件 WSL 没装(暂阻)→ 攻 LLM-assist(qwen key 在)。`repoprobe/llm.py`(DashScope 兼容,纯 urllib)+ `boot.py` 接(heuristic→问 LLM 升级 plan)+ `sandbox.py` 认 `method=llm` + `_sample_noconv` 测样(server.py,detector 认不出)。**实测**:`RP_LLM_ENV_FILE=…/skills-studio/api/.env python3 -m repoprobe repoprobe/_sample_noconv --sandbox localdocker` → **LLM 判出 Flask:7000 → 真 boot + 探 `/ping`=200,22.8s**(env-file fallback CR-safe = 可靠复现)。40+1 单测无回归。**= RepoProbe 现能跑无运行约定的 repo(v2 头号特性达成)。** **✅ compose 多服务也落**(装 docker-compose-v2 v2.40;`sandbox._boot_compose` 真 `docker compose up -d --build` 起整栈〔web+redis 都 Up〕→ `compose ps` 找端口探 → `down -v` 拆栈零残留;probe 超时 3→6s)。⚠️ **web→redis 容器间网络在本 WSL dockerd 不通**(iptables-legacy 没放行 compose user-bridge FORWARD = env 问题非 RepoProbe;RepoProbe 正确标 /cache "崩"),全绿需授权放行 FORWARD。**剩 v2**:egress 锁定 / surface 非声明式路由 LLM 推断。**086 共编已核:我的 library_unit + 侧线 SETTLEMENT_WORKERS/VARCHAR 共存,没冲掉。**
>
> **▶ WSL Docker(每次 WSL 重启后要重起 dockerd)**:
> - 起 dockerd:`wsl -d Ubuntu -u root bash -lc 'pkill dockerd; nohup /usr/bin/dockerd >/tmp/dockerd.log 2>&1 & disown'`
> - 跑 RepoProbe(CLI):`wsl -d Ubuntu -u root bash -lc 'cd /mnt/d/projects/skills-pilot && python3 -m repoprobe <repo> --sandbox localdocker'`(原生 docker 在 `/usr/bin`,已排 `/mnt/c` Desktop shim 之前)
> - **🌐 本地产品(web UI)= http://localhost:8900**:Bash **run_in_background** 跑 `wsl -d Ubuntu -u root bash -lc 'cd /mnt/d/projects/skills-pilot; export RP_LLM_ENV_FILE=/mnt/d/projects/skills-studio/api/.env; exec python3 -m repoprobe.server 8900'`(零依赖 stdlib;WSL2 自动转发 localhost→Windows;丢 repo 路径→看报告;web 里也能用 LLM-assist;⚠️ **必须 `export`**——旧 `VAR=val exec` 写法不把 env 传进进程→LLM-assist 静默失效〔2026-06-04 坐实的 0.0s bug〕)。**本 session 已起后台任务,localhost:8900 直接可用**。注意:`nohup&disown` 在一次性 wsl 调用里不存活,必须 run_in_background 托住;`pkill -f repoprobe.server` 会自杀别用。
> **🔗 v2 远程 repo(本地+远程都支持)**:`repoprobe/fetch.py` `resolve_repo` —— git URL(`https://github.com/...`/`git@`/`*.git`)→ `git clone --depth 1` 临时目录 → 跑验 → `finally` 清理;本地路径原样。`boot.py` 已接(report 显原始 URL)。**三验通**:octocat mock(克隆+分析)/ crccheck localdocker(真克隆+build+run 45.9s)/ web UI POST URL。CLI + web 全打通。40+1 无回归。
> **🎯 闭环实证(强 · 答"设计/实现漏洞能否 skills 优化掉")**:用户点出 detector cli-误判这类洞用例当时就列了(02-prd「v1 第一类=Docker web 服务」)、理论上该有设计 = 设计→impl 保真度掉(Signal #5),且 03-tech-solution **L133 当时自标**「auto-boot 启发式无专门 skill 覆盖」。**跑闭环**:032 `AH-` 从需求钉 detector 4 断言(`工作产物/12`)→ **不知情子 agent 盲跑 093 built-vs-spec** → **1 fail/3 pass**:精确抓出 `_guess_kind` 只认依赖关键字、无视 EXPOSE/启动命令(+漏 gunicorn),**自构反例**,**还白捡 2 个我不知道的洞**。**= 答案"能"已实证:验证脊(AH-@032 → built-vs-spec@093)盲跑机械抓真洞+file:line,doc-vs-doc/合成 eval 抓不到;条件=设计把用例钉成 AH-,短板在设计 skill 完整性(L133 自标)。用 RepoProbe 真洞正面验 Signal #5/#6 的解。** **续 → 修+再核走完闭环**:按 AH- 修 detector(`_guess_kind` 三信号 + `detect()` 跨分支补判 + compose.yml + pkg 边界)→ **盲核 #2 抓出我修不全**(gunicorn-only→unknown)→ 修全 → **盲核 #3 AH-D01 PASS**(5 case 全对)。48 单测(+8)无回归,live 复核确认(`工作产物/12`)。**3 个独立盲核 agent 把关 = 验证脊真机械核对、连半吊子修复都挡得住。** ⚠️ live server 坑:run_in_background 的 wsl server 脱离任务追踪会残留,清理按 PID `kill -9` 别按名 pkill(自杀)。

**Pilot 1 = 用 agent 跑真实产品的完整 SDLC**(D-004-OVERRIDE:砍了 Skills Studio 造壳路线;agent 就是 skill 的 runtime,不再造工具)。
产品 = **RepoProbe「零配置自动跑验」**:丢 repo → 自动 boot + 戳功能 → 报告"能跑吗/产出啥/哪崩哪不合理"。

**本 session 进度**(工件全在 `D:/projects/skills-pilot/`,全程 agent 直接调 skills 跑 = 真 dogfood):
步0 可行性✅(`00-feasibility`,挡了 explain-repo / 找烂码 两个红海)→ 步1 PRD✅(`01-breakdown`+`02-prd`)→ 步2 技术方案✅(`03-tech-solution`)→ 步3 研发开跑:`repoprobe/`(detector + sandbox[Mock/LocalDocker/E2B] + surface-prober 路由发现),**Mock 验通**;N210 自审抓到真 bug CR-01(容器泄漏)已修(`04-code-review`)。

**🔀 FORK 已拍 = B(session #4)**:补 skill 头号洞「spec↔现实验证层」。**📌 汇报口径(用户 06-02 校正):这是对 N080/N260 两个现有节点的 targeted 优化(填 D-003 缺口),非净增 skill scope——对外/日报统一说"优化现有 skills",不说"新建 skill"。** 进度:
- ✅ **skill #1 `ui-spec-generation` 已建**(`完稿/N080 原型解析/ui-spec-generation/`:SKILL.md + output-template + scoring-rubric + N080 契约)。定位 = N080 **Stage-C 合成**:018-021 拆解 → 它把 `P-/FT-/ACT-/FLD-/OBJ-/SM-` 合成为 binding 契约(五维:data/action/state/permission + **`AH-` 验收断言**)。3 模式含 `from-requirements`(解 Signal #4 的"没原型只剩文字/状态机")。
- ✅ **dogfood 验通**(`skills-pilot/skill-fork-b/cinemaai-ui-spec-dogfood.md`):真 CinemaAI 原型 + N070 跑出 2 页(共 13)binding 规格,产出 018-021 产不出的「OBJ-/SM- 绑定 + 9 条 AH- 断言」,两 gate-critical 维满分。命门 `AH-gen-01`(调外部 API 前必须确认费用 F-022-R02)+ `API-MISSING` = CinemaAI 类 spec↔reality 雷的精确定位。
- ✅ **skill #2 `built-vs-spec-consistency-check` 已建**(`完稿/N260 质量门禁与专项测试/built-vs-spec-consistency-check/`:SKILL.md + output-template + severity-and-verdict)。N260 **reality gate** = 整个 SDLC 套件**此前不存在的一类**门禁(其余全是 doc-vs-doc);消费 `n080.ui-spec` 的 `AH-` + 可插拔 `reality_adapter`(runtime-observation/static-frontend/e2e-trace/manual),逐条判 pass/fail/**unknown(needs:<adapter>)**,绝不 fake-pass。
- ✅ **闭环 dogfood 验通**(`skills-pilot/skill-fork-b/cinemaai-built-vs-spec-gate-dogfood.md`):adapter=`static-frontend` 跑真 CinemaAI 原型 → **3 pass / 0 fail / 6 unknown**(verdict `conditional`)。两个硬结论:① 门禁**自己算出** 6 条红线/行为断言 `needs:runtime-observation` → "要权威 verdict 必须上 RepoProbe" 是机械产出而非论断(**A↔B 合流硬证**);② 门禁**反证纠正了 spec 的过时假设**(AH-gen-01:spec 标"原型未见 modal",真原型 L5991 其实有)→ reality gate 的**双向价值**,合成 eval 永远抓不到。
- ✅✅ **真代码核对(最强结果)**:用户指出 `D:/projects/python/ai_work/video/video_ai` = CinemaAI **真实全栈实现**(Next.js+FastAPI+Celery,**自带 `.skills_workspace` = 团队用 skill 库建的它**)。门禁 `reality_adapter=code-static` 跑真代码 → **coverage 0.94 · verdict `no_go`**(**团队复核后:4 真红线 + 1 撤回**):失败不退款(`refund` 全库零调用,**波及所有 task 类型**)/ 成功不落库不 commit(worker stub)/ suspended 前端不拦(editor 不查 billing)/ 预扣不对账(`commit_charge` 仅注释)。~~预扣竞态超扣~~ **撤回**:`get_db` 末尾单 commit + SQLAlchemy autobegin 使 `with_for_update` 锁横跨整个请求 → 不超扣、F-060-R01 实满足(我把"无 `db.begin`"误推成"锁失效")。**元教训:concurrency 后果要按事务模型验、非 grep;我标"亲核 high"的那条恰恰错了 → 高置信断言也要对抗复核**。报告 `skill-fork-b/cinemaai-built-vs-spec-gate-video_ai-REAL.md`。
  - **Docker reframe 坐实**:code-static 零 Docker 给出权威 verdict;之前"需 RepoProbe runtime/Docker"被真代码取代(runtime 仍是未来 adapter 选项,非必需)。
  - **价值实证(逼近 G2)**:门禁在真 shipped 代码里逐条抓出**会丢钱**的实现缺陷——doc-vs-doc 门禁(N100/N260/044)+ 合成 eval 永远抓不到。坐实 Signal #5(spec 强、链路漏)+ D-003(impl≠spec)。⚠️ 诚实:video_ai 早期 sprint(多处 TODO),故部分是"未接线"、BLK-03 是真 bug;但都属"上线前必修"。
- ✅ **缺陷清单已产出**:`skill-fork-b/video_ai-defects-for-team.md`(7 issues:P0×3 资金红线 + P1×3 + P2×1 + 1 spec-drift,全带 file:line + 修复建议 + 验收,可直接贴 issue)。写时又挖深一层 ISSUE-4:`commit_charge` 即便被调也不回补余额差额(F-060-R02 多退少补双重未实现)。
- 🎯 **G2 首个数据点已回(06-02)· 见 D-017 + `skill-fork-b/video_ai-defects-dev-adjudication.md`**:团队研发裁定 + 真 Postgres 集成测试(14 passed/全量 227)→ **6 真/1 误报(ISSUE-3 已自纠)/novel=2**,并**反向修正审计 3 处**(outbox 修法会进 DLQ/双重计费被汇总口径守住=高估/test_billing_race bitrot)。对判据:误报✅·novel❌(2)·有用~隐性。**裁定:精度高+真参与,但低于 novelty 门槛 → 价值=上线前红线巩固非新发现;混合偏正、非铁证**。**→ G2 首轮闭环(D-018)**:团队显式答 = **值得跑,但定位 = 上线前/周期「发现器」+ 人工裁定 + 确认项沉淀成确定性测试,不做 per-PR CI 硬门禁**(擅抓单测测不到的"未接线"红线;但定级/运行时是弱轴、会自信错)。= **合格正信号(限高风险模块上线前)= 北极星首个真人价值证据**,非全链外推。〔已执行〕#6 刻画完毕、不建 skill #3:把 `skill-fork-b/video_ai-defects-for-team.md` 送达 video_ai 计费/后端 owner,作为**真人价值微实验**。测量 = {novel 条数 / 真问题数 / 误报数 + 一句“这种 spec↔code 自动核对对你们有用吗”}。判据:**≥3 条 novel-真问题 + ≤1 误报 + 对方说有用 → G2 首个正信号**(北极星首次真人证据);反之诚实记 D-004 风险。⚠️ **送达是人工社交动作(我做不了)**;deliverable + 实验设计 + 开场白已备好,球在 builder 手里。
- 🔄 **D-019(用户 06-02 拍板)· 选 A · re-home ✅ 完成(2026-06-02 · 验证无重复、净增 0)**:**不增 skill**,把 2 个新 skill 的能力**折叠进现有 skill**,净回 **155**:
  - `ui-spec-generation` 的 **AH- 验收断言** → 折进 N110 **`032-acceptance-criteria-generation`**(让验收标准变成可机械核对 = AH-,治 Signal #4 于源头)。
  - `built-vs-spec` 的核对 → 折进 N260 **`093-quality-gate-check`**(加 `built_vs_spec` 维度 + D-018 discoverer-not-gate 模型)。
  - 折叠后**删除** `完稿/N080.../ui-spec-generation/` + `完稿/N260.../built-vs-spec-consistency-check/` 两条独立条目。
- ✅ **G2 首轮闭环(D-018)= 合格正信号(限高风险模块上线前)= 北极星首个真人价值证据**:门禁定位 = 上线前/周期「发现器」+ 人工裁定 + 确认项沉淀成确定性测试(非 per-PR CI 硬门禁);已固化进 skill v1.1.0(将随 A 搬进 093)。非全链外推。
- ⚠️ **北极星校准(D-019)**:本 session 默认在"建/加"(建了 2 skill),项目约束是"优化/减"——已纠,后续提案先问"能否优化现有 skill 达成"。
- **A · RepoProbe(已重新动起来 · 06-03 #2)**:SDLC 走完**测试设计(N230)+ 缺陷管理(N250)**两阶段,有了 **40 测试 + 1 xfail 的 pytest 套件**(`skills-pilot/tests/`)+ 缺陷包(`工作产物/05`、`06`)。剩:N270 发布就绪可继续 dogfood;DEF-1 修复 trivial(~5 行)可作 dev 演示翻绿 xfail;真 boot 仍卡 Docker(daemon down)+ 无 E2B key(两 adapter 代码就位)。注意:**A 现在是 B-gate 的 reality feed**,不再是纯并行选项。
- **🔥 Signal #7(06-03 #2 · target/形态 覆盖洞 · 三步证据 N230+N250+N270)**:**设计/分析层 skill(080/082/083/090/091/092)target-agnostic、强**;但**产出物/归因层有隐性形态预设** → 换形态掉槽:① N240 `086`(产可执行测试码)绑死 OpenAPI/HTTP → 库/CLI/SDK 无 runnable 单测生成 ② N250 `089`(失败归因)偏 CI-失败驱动 + 示例/taxonomy 自相矛盾(C2)+ 缺潜伏缺陷槽 ③ `091` 严重度公式预设"已上线有用户"。同 infra #2/#3 族。**候选优化(非现做,全走加 mode/补槽,守 D-019)**:086 加 `library_unit` mode 消费 080 输出;089 补 C7=latent_product_defect + ~~修 C2 示例~~ **✅ 已修(14 处标签→canonical,re-zip 回库验净,git 可回滚 = Pilot 首个修-skill 闭环)**。**剩候选**:089 加 C7 槽 / 086 加 `library_unit` mode / 105 加 `untrusted_input_execution` 维 + 104/103 非服务目标降级 / ✅ **已修 validator utf-8(`validate_skill.py` × 24 zip〔076-099〕批量加 `encoding="utf-8"`,验证净、两变体实跑通;`validate_artifact.py` 证伪不在内)= Pilot 第 2 个修-skill 闭环**。**只记,别又用补 gap 顶替 G2(已连 3 阶段磨刀)。**

**真跑前置**:Docker Desktop 引擎(本 session 一直没起 → LocalDocker 跑不了)/ E2B key(无,adapter 就位)/ RepoProbe 的 LLM key 待配。

> Skills Studio(旧载体,已弃,代码留参考)的"起服务"命令在下方「▶ 本地跑起来」块。🔥 Signal #4 / 🔴 价值未验 / 📌 优化 skills 是过程记录,后两块已被本方向收编。

## 🔥 Signal #4(最大 · 来自 CinemaAI 实战回顾)

CinemaAI:skills 产 PRD → 团队 ship,但**前端 UI 与 PRD 完全对不上**。根因 ① 无 skill 生成 binding 的 UI 规格(N080 把原型当输入,没原型就只剩文字/状态机)② 无门禁验 built-UI-vs-PRD(门禁只查文档质量)。
- **收敛 meta-pattern(#2 infra + #3 进程生命周期 + #4 UI 都指向同一根)**:**skill 擅长产上游文档,但无机制保证"下游现实(UI/infra/运行)对齐文档"。门禁查文档质量,不查文档 vs 现实。**
- → **skill 优化头号方向**:补"UI 规格生成"skill + 加"built-vs-spec 一致性"门禁(UI 和 infra 都要)。
- 也是 RepoProbe **v2「验自己项目 vs spec」**的真痛证(同一 spec↔现实 命题);**v1 不动**,进 v2 backlog。
- ⚠️ **合成 eval 永远抓不到这个**(只比工件 vs 工件,不比工件 vs 真 ship)→ 只有真 ship 暴露,再证 D-004-OVERRIDE 的"真跑真 ship"对。

## 🔥 Signal #5(诊断性 · session #4 · D-003 失败的上游机制)

用户实战观察 + CinemaAI N120 工件验证:**PRD→技术需求(N090→N120)结构性丢失「操作 / 界面字段 / 整条链路」保真度。**
- **实证**(`cinemaai/.../N120/工程需求解析.md` + `API意图清单.csv`):
  - N120 `036 engineering-requirement-parsing` 是**横向抽象**,`source_artifacts` 含 N070/N100/N110 但**不含 N080**(ACT-/FLD-)→ 操作粒度(锁定/插入/复制镜头)塌成几个 API;`triggers` 只剩 user_create/archive;**界面字段层完全缺席**(ER 只到 OBJ-,无 FLD-)。
  - **无任何纵向链路工件**(feature:UI字段→动作→API→service→数据→状态);detail 散在 4+ 横向工件,无人拼装。
  - **双向漏的铁证**:ui-spec dogfood 标的 `API-MISSING`(生成前预估费用)其实是 N120 的 `API-045 /generate-estimate`——ui-spec 看不见 N120 的 API,N120 看不见 N080 的字段。工件横向铺开、**无纵向交叉引用**。
- **意义**:这是 D-003「ship 前端 vs PRD 脱节」的**上游机制**。Fork B 补了两端(N080 ui-spec + N260 门禁),**中段 N120 仍漏,且 N120 不消费 ui-spec**。与 Signal #4 同根(handoff 保真度),新轴 = 转换链信息损耗。
- **targeted 修法(若做 · 非新 skill)**:① N120 036/037 契约消费 N080 ACT-/FLD-/ui-spec(加 `source_act`/`source_fld`/`ui_ref` 列)② 可选"feature 纵向 trace"聚合视图(可走 aggregator 模式,非新原子 skill)。
- ⚠️ **这是连续第 3 个 skill-gap 信号**(infra #2/#3 → Fork B → 本条)。库被真用就会无限暴露 gap(健康),但**别让"补保真度"再次顶替"证明有没有用"(G2)**——见下方 🔴。

## 🔥 Signal #6(无原型 → 功能清单不全 · 来自真实使用 · 可能最根本)

用户实战:**PRD → 设计 → 代码,在无原型图时,生成的功能清单系统性不全、丢很多。**
- **机制**:原型是**完整性的强制函数**(画屏就被迫定下每个字段/动作/状态/次级页)。无原型时,功能枚举 = PRD 文字所述 + LLM 所推;**人写 PRD 必漏"显然项"**——列表的搜索/筛选/分页/空态、实体的编辑/删除/详情、异步动作的状态/错误路径、各角色受限视图、设置/通知/审计/帮助。这些"长尾"只有画 UI 时才被迫显形。
- **链路缺口**:N070 `requirement-breakdown` **只结构化已给的**,不系统**推导**应有面;N080 唯有原型才强,其 `inferred-from-prototype-absent` 是显式 lossy fallback;N100 `025-requirement-completeness-check` 多半查**文档完整性**(章节齐/无 TBD)≠ **覆盖度推导**(待核)。→ 无原型时,**全链路无人做"实体×{CRUD/list/detail/edit/bulk}×状态迁移×角色×横切屏"的覆盖推导 + 差集"**。
- **轴**:这是 **spec 完整性(intent→spec)**,区别于 Fork B 的 **spec→code 保真度**。两轴互补:门禁查"spec 里的都实现了吗",本信号是"该有的都进 spec 了吗"。Fork B 的 ui-spec `from-requirements` 能展开一部分面,但**继承上游枚举的不全**。
- **假想修法(若做)**:一个"功能覆盖推导/门禁"——derive-then-diff(同 095-099 测试点展开、同 built-vs-spec 的 derive-then-check 形状),挂 N070/N080/N100;**优先非新原子 skill**,先验 025 到底查什么。
- ⚠️ **连续第 3 个 gap(#4→#5→#6)同 session**;**别在 video_ai findings 送达团队(G2)之前建 skill #3**。
- **实测(hub-oa 真项目 · 06-02 · 部分证实 + 两次差点 overclaim)**:派 3 Explore agent 盘点 PRD/前端/后端。
  - **inventory-count diff 不能证 #6**:PRD = 24 菜单/130 叶 + 436 feature-ID + 18 模块 PRD(B2 审批一个就 3544 atom)vs 实现 = 220 前端页 + 415 控制器/2180 端点。**差大但主要是粒度展开**(1 菜单→多页→多端点),且 PRD **并不薄**。
  - ⚠️ agent 报的"781 watchdog 违规"我核实 = **RBAC 越权(角色看到不该看的菜单),非功能缺失**——差点头条误引(P0-3 同款,本 session 第 2 次 agent 证据 overclaim)。
  - ✅ **targeted 探针证实 #6 在"子功能/页面粒度"real**:黑天鹅雷达 PRD = 1 菜单叶 + 散见提及、**无专属模块 PRD**,代码 = 11 前端页 + 8 控制器。→ **#6 形态 = "每个功能下的页/动作/状态长尾未枚举",非"整功能消失"**。量化需 targeted feature-level diff(黑天鹅探针=方法)。
  - 📌 **OA 团队已自建 menu-consistency watchdog** 在处理 PRD↔实现漂移 → #6 在真实世界确有其事 + "覆盖度核对"已有真实先例。
  - 🔁 **元教训(本 session 第 2 次)**:agent/静态报的"证据"头条引用前必须自己核实——两次都被我核出 overclaim(P0-3 竞态、781 watchdog)。我的分析跑在验证前面了。

## 🔴 当前最重要的事:价值未验(别被"判据近全绿"骗了)

**builder 自测后说"感觉没什么用 / 不知道作用是什么"。** 技术判据 G1/G3/G4/速度都绿,但那是**技术绿,不是价值绿**。

诊断(不是产品死刑,是测法错位):
- **输入是玩具**:一句话"会议室预订"。CinemaAI 是**真实详细 PRD** → 才出 41 个真用工件。GIGO:一句话进 → 通用草稿出。
- **评的人坐错座**:builder 不写 PRD,给不写 PRD 的人看生成的 PRD,必然"so what"。这正是 **D-004 自造 Pilot 的内置盲区**(builder ≠ 用户)。
- **没对照**:手写 2 天 vs 96 秒草稿,省没省没量过。

**结论:别再加功能(解不了"没感觉")。下一步二选一 ——**
- **A(荐)· 真价值实验**:找一个正开新项目的人,用**真实详细输入**(非一句话)+ qwen-plus,跑一遍,问"比白手起家省事吗"。这是唯一能答"有没有用"的实验 = G2 的正确打开方式。
- **B · 诚实面对 D-004**:找不到那个人 → 自造 Pilot 证不了价值,记成方法论 learning,换真业务场景重做 Pilot。

> 北极星:目标从来不是"builder 觉得有用",是"**小团队能不能用它更快 ship**"。CinemaAI 已证系统有用(真 PM PRD→41 工件→13 人 ship alpha);缺的只有"真人用低摩擦入口"这一次实验。

## 📌 新方向(session #3):用户想优化/提升 155 skills(不冻结)

- ⚠️ **冲突**:wholesale「重写全部 155 / 重写所有 description」= ROADMAP anti-goal(复议时点 Phase 3)+ 跑偏检测项;北极星「不增只减、单线推进」。**别整体重写。**
- ✅ **合法版 = 数据驱动 + targeted**:跑 `_eval` baseline(D-003 CinemaAI ground truth;**现在终于有 Qwen 模型可真跑**了)→ per-skill 评分排名 → 只改最低分 + 最常用的几个 → re-eval 量 delta。这正是 eval 框架当初建的目的。
- 🧭 **排序提醒(北极星)**:产品价值(A/G2)仍是更大的未答问题;优化 skill = 磨刀,先确认有人要这把刀。eval baseline 可与价值实验并行,但**别 wholesale 重写**。
- 下一步候选:跑 eval baseline(先 1 任务,如 `CINEMA-N070-requirement-breakdown`,`--adapter openai`/qwen-turbo)。⚠️ D-012 caveat:GT 可能是别的模型产的 → 绝对分有偏,但**同模型下的相对排名仍能定位弱 skill**。

## 当前阶段

**Phase 1 · Pilot 1 · 改版(D-004-OVERRIDE):用 agent 跑真实产品的完整 SDLC**(想法→可行性→PRD→研发→测试→部署→反馈,见 ROADMAP Phase 1 改版)。**步 0 已跑完(首个真 dogfood!)**:pilot 产品 = **代码行为速验工具**(PM 真痛:快速摸清陌生 repo + 看它跑出啥)。用 competitor/value/risk 三个 skill + 真 web 搜 → **conditional-go**:🔴 "解释 repo" 红海(DeepWiki 免费)NO-GO;🟢 "一键跑起来看实际行为" 窄缝 GO-IF(需收窄 niche)。产物 `00-feasibility.md`。→ **步 1 breakdown 出**(`01-breakdown.md`)。**产品身份经 3 次 reframe(学→批→测)收敛并锁定 = 「零配置自动跑验」**:同一引擎(auto-boot 任意 repo + 观察行为),job = 能不能跑/行为/异常,学&批 = 副镜头;**非全量正确性 QA**(陌生 repo 无 spec=无 oracle);内部 repo = v2。⭐F013 结果锚定 + ⭐F023 安全=命门。**🛑 停止 reframe:新点子进 v2 backlog,不动 v1**。→ **PRD 出**(`02-prd.md`)→ **Path B 技术方案出**(`03-tech-solution.md`:三级 boot ladder + E2B sandbox-adapter + surface-prober + 安全命门 + 4-6 周任务)。**步 3 研发开跑**:boot 引擎骨架建好 + **Mock 验通**(`skills-pilot/repoprobe/`:detector 正确识别 Dockerfile/约定 + sandbox adapter[Mock/LocalDocker/E2B 可切] + 编排串通)。**真跑待环境**:Docker 引擎没起(LocalDocker 跑不了)+ 无 E2B key,两 adapter 代码就位。Week2 **surface-prober 建好+Mock 验通**(`surface.py`:静态发现 Flask 路由 ✓ `/`+`/health`,接进编排;HTTP 触发待 boot)。③ **N210 review 完成**(`04-code-review.md`):**抓到真 bug CR-01**(LocalDocker 超时泄漏容器)→ **已修**(唯一 tag + 超时 rm -f);7 findings。**第 3 优化信号**:N210 偏 Java + **缺"外部进程/容器·资源生命周期"风险类目**(抓不到 CR-01 那类 bug)。**与 #2 同源 → 整套 SDLC skill 对 infra/sandbox/进程类项目覆盖弱**(给规划/设计/审查三层加 infra 维度 = 真优化方向)。剩:起 Docker 验真跑 / Week3 LLM-assist(surface 触发)。🎁 已收第 1 个 skill 优化项:competitor-analysis 的 scope 步骤该加"地域/市场"必填(我差点漏国内竞品)。**Operator = 1 人全栈**(产品+研发+测试+运维)= 北极星 N=1 最小团队;skills = 跨角色增益,价值检验 = "带 skills 比纯靠自己 ship 更快/更稳吗",最吃力的角色 = 最该优化的 skill。无"拉工程师"环节。Skills Studio(旧载体)代码留参考、不再投入,服务可关。

## ▶ 跑起来(局域网模式,每个新 session 都要重起)

架构:前端 `/api` 经 Next rewrites 代理到后端(`next.config.mjs`),所以**访客访问 `http://<服务器IP>:3000` 即可**,API 走同源、不写死 IP、无跨域。后端只绑 127.0.0.1(Next 同机转发)。

```bash
# 后端(读 api/.env 的 qwen-turbo + key;skills 已在 db,无需重新 sync)
cd D:/projects/skills-studio/api && SS_LLM_MODEL=qwen-turbo \
  SS_DB_PATH=D:/projects/skills-studio/skills_studio.db \
  SS_ARTIFACTS_DIR=D:/projects/skills-studio/artifacts_store \
  python -m uvicorn app.main:app --port 8000   # run_in_background,绑 127.0.0.1
# 前端绑 0.0.0.0(局域网可达)
npm --prefix D:/projects/skills-studio/web start -- -H 0.0.0.0 -p 3000  # run_in_background
# 端口被占:netstat -ano | grep ":8000\|:3000" → taskkill //F //PID <pid>
```
**局域网访问:http://192.168.77.117:3000**(本机 LAN IP,以太网2;IP 变了用 `ipconfig` 查)。
⚠️ 别人连不上多半是 **Windows 防火墙**:管理员 PowerShell 跑
`New-NetFirewallRule -DisplayName "SkillsStudio3000" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow`

## 即将做的事 ← LOOK HERE FIRST

**Pilot 1 判据近全绿:G4 初验✓ · G3 5/5✓ · 速度✓(turbo 96s) · G1 本地✓ · 可读性层✓(D-014)。剩:G2(拉 CinemaAI 1 人试)—— 现在 UI 有大白话导览,拉人试不会一上来就懵了。docker 不做,可选 Path B-E。**

> 用户反馈"不懂/不会用/看不懂结果"→ 已加可读性层(D-014):大白话名 + 工件人话标签 + 折叠机器细节 + 自动阅读导览 + 3 步引导。新 build 已在 localhost:3000。

模型:DashScope 兼容端点,**默认 qwen-turbo**(D-012;api/.env 写的是 plus,运行时 inline 覆盖成 turbo;docker root .env 已是 turbo)。6 次真跑工件留底于 `artifacts_store/`。

### Phase 1 判据现状(G1-G5)

```
🟢 G4 质量 · 初验通过(turbo + prompt_call + 富上下文,工件达标 → D-013 agent 不开)
🟢 G3 · valid_data_points 5/5,failure 0%
🟢 速度 · turbo 96s,达 <5min NFR(D-012)
🟢 G1 · 本地 localhost:3000 可访问可点(已满足"任意可点形式")
🟠 G2 · 拉 CinemaAI 1 人真用过 ← 最后一块硬判据,需 outreach
⚪ docker · **不做**(用户 2026-06-01 决定);compose/Dockerfile 留作未来可选
🟡 次要:B10 SSE / B13 真 auth / catalog 搜索 / Path B-E(D-011 stretch)
```

### Week 3 完成判据(达成)

- [x] 全栈跑通 + **真模型出 4 份高质量工件**(context-brief evidence-tag、breakdown 5 层树 + 上游正确流入)
- [x] 富上下文注入(D-013 prompt_call)质量验证 → **agent 模式不需开**(省成本)
- BD-01:实现全顺 → **方案 A(全量),不砍 scope**

> 北极星信号:**一句话需求 → 经 Web 工具 + 便宜模型 → 4 份可用工件**,核心价值假设拿到强证据。

### Week 1 完成判据(已达成)

- [x] 4 份产物存到磁盘(+ INDEX,共 5 份)
- [x] PRD 通过自我评审(review-agenda gate 自评 = conditional-go,诚实给分)
- [x] 跟 Skills Studio 范围对齐(MVP 22 叶 / STRETCH 10 / OUT 2)

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

### 🔴 P0 · 立即做 / 启动 Week 3

- [x] ~~Path A 跑 PRD~~ → ✅ 4 工件 + INDEX(`工作产物/`)
- [x] ~~Path B 技术方案~~ → ✅ 5 件(`工作产物/tech-solution/`),gate ≈84.3
- [x] ~~目录 / 栈 / MVP 范围 / 模型 / 执行模式~~ → ✅ D-009~D-013
- [x] **B01 脚手架**:Next+FastAPI+docker-compose,`D:/projects/skills-studio/`(api/+web/)
- [x] **B03 sync-skills**:156 zip → 155 skill / 40 节点 / 5 path 入库,6 端点通
- [x] **B05/B06 ⭐ orchestrator**:通用 PathRunner + NodeExecutor(prompt_call + SKILL.md 富上下文)+ Path A 4 步;**Mock 下端到端出 4 工件 + 门禁暂停/放行 + telemetry 全生命周期**,实测
- [x] **B07 门禁** + **B08/B09 工件读**(随 B05/B06 一并落:gate confirm、artifacts list/content 端点)
- [x] **B04 前端**:3 页 + 共享 api 层,浏览器 live 验证全流程通
- [x] **可读性层(D-014)**:大白话 path 名 + 工件「是什么/给谁看」标签 + 折叠契约 YAML + **自动阅读导览**(`/guide`,实测纯大白话)+ 3 步引导 → 解"看不懂结果",**G2 去风险**
- [x] **B02 adapters** + **R4**:OpenAICompatible 真跑 **qwen-plus** 成功(`api/.env`),4 工件达标
- [x] **G4 初验**:真工件质量达标 → agent 模式不需开(D-013)
- [x] 🟢 **速度**:实测 qwen-turbo 96s(vs plus 6-7min)→ 默认 turbo,NFR 达成(D-012)
- [x] **G3 ✓**:valid_data_points **5/5** · failure 0%(plus×1 + turbo×4,真 Qwen,93-167s/次)
- [—] **B14 docker**:**不做**(用户 2026-06-01 决定);**G1 由本地 localhost:3000 满足**。docker-compose/Dockerfile 留作未来可选,根 .env(冗余 key 副本)已删
- [ ] 次要:B10 SSE / B13 真 auth / catalog 搜索

### 🟠 P1 · Week 1 期间穿插做

- [ ] 装 `openai` SDK(`/c/ProgramData/miniconda3/python.exe -m pip install openai`)+ 配 DeepSeek/兼容 key(D-012)
- [ ] `adapters.py` 加 `OpenAICompatibleAdapter`(换 base_url+key 即切 DeepSeek/Qwen/GLM)
- [ ] 跑 eval baseline:**先 1 个任务**(`eval.py --adapter openai-compat --only CINEMA-N070-requirement-breakdown`)
- [ ] ⚠️ 注意 ground truth 对齐:CinemaAI 41 工件是哪个模型产的?(D-012 caveat,影响分数解读)
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
| LLM key(改用免费/已有 DeepSeek/Qwen,D-012)| 我自己 | Week 3 前 |
| Skills Studio 部署到哪不确定 | 我自己决 | Week 3 |

## 开放问题(随时可决,不阻塞主线)

- ~~Skills Studio 用什么栈?~~ → ✅ Next.js+FastAPI(D-010)
- ~~Skills 调用直连 Anthropic 还是 proxy?~~ → ✅ 直连免费/已有兼容模型(D-012),proxy 不做
- 权限模型?(MVP 单租户 vs 多租户)← 仍开,TD-02 待定(不阻塞)

## 跑偏检测(给未来 Claude)

如果用户开始做这些事,请按 CLAUDE.md "应该做的事 #3" 主动拉回:

- 讨论"再加一批 skill"
- 讨论"重写所有 description"
- 讨论"是不是该转方向"(在 Phase 1 还没完成时)
- 讨论 path D 或 E 的优化(没数据,不优化)
- 讨论 Claude Skills marketplace 发布(Anti-goal)
