# 📨 HANDOFF · 验证侧线 → RepoProbe 主线(2026-06-03)

**给主线 #2**:验证 arc(本侧线)已收口,**侧线即日起不再编辑 155 库**。你是库的**单一编辑者**了。下面是侧线对库做的**全部** skill 优化(均 D-019 净增 0,库始终 **157 zip**)。动其中任何一个前**先从当前库 zip 重新 `Expand-Archive`**(含侧线改),再改再压 —— 否则"最后写者赢"会冲掉对方。

---

## 🔴 唯一活跃冲突点:086(你我都要改它)

- 侧线**已折入并验通在库里**:`086 full_chain_integration` 的「realism 纪律」后多了一个「**真用补充**」子段(D-021 反哺):
  - ① **真 DB(非 mock)才抓列宽/约束/类型 bug** —— VARCHAR(20) 铁证(create2 `task_type` 22 字符 → 生产 500)→ 全链集成测试用真实 DB 引擎。
  - ② **结构护栏参数化覆盖所有 money/settlement 路径**(`SETTLEMENT_WORKERS` 模式)= 该进 CI 的确定性护栏。
- 你 STATUS 行 17 的下一步 = 给 086 加 `library_unit` mode(消费 080 测试点 → pytest 骨架)。**那是另一段,与「真用补充」不冲突** —— 但你**必须从当前库 zip 重新 extract** 再加,否则会冲掉它。
- ⚠️ **别用 `_rehome_work` 做 086 的临时目录**:侧线折 086 时,Edit 文件态在 `_rehome_work` 上反复打架(疑你也在用它)→ 侧线改用隔离目录 `_086fold` + 原子 extract→edit→`Compress-Archive -Force`→重展验证 才成功。建议你也用独立目录。
- **改完自检锚点**(086 SKILL.md 里都应各 ≥1 命中):`真用补充` / `VARCHAR(20)` / `SETTLEMENT_WORKERS` / `full_chain_integration mode` / `library_unit`。

---

## 侧线已折入库的全部 6 处(完整清单 · 你接管维护)

| skill | 加的 mode / 字段 | 验什么 | 冲突? |
|---|---|---|---|
| `032 acceptance-criteria-generation` | `acceptance_hooks[]`(AH-)+ §可核对验收 | 断言**从哪来** | 否 |
| `093 quality-gate-check` | `built_vs_spec` 维度 | 静态结构断链 | 否 |
| `113 trace-call-chain-analysis` | `chain_completeness_verify` mode | 链**走通**+断点 | 否 |
| `112 log-analysis` | `chain_completeness_verify` mode | 走通(无 trace fallback) | 否 |
| `086 api-test-script-generation` | `full_chain_integration` mode **+ 真用补充段** | 结果**对** | **🔴 是(见上)** |
| `088 test-automation-orchestration` | `full_chain_verification_playbook` mode | 编排四法 | 否 |

> 这 6 处串成一条「全链执行验证」spine(静态 093 → 走通 113/112 → 对 086 → 编排 088,断言源 032)。也单独打成了 plugin:`D:\projects\skills-pilot\fullchain-verify-pack\`。

---

## 你的优化管线(STATUS 行 17)与侧线的重叠面

- **仅 086 重叠**(上面那一格)。`054 untrusted_execution`(你已做)/ `089 C7 槽` / 遥测簇 `no_telemetry` = 你独占,侧线没碰。
- 所以协调成本就这一处:**086 重 extract 再加 library_unit**,完事。

---

**侧线承诺:不再编辑库。** 这份清单 = 库当前真状态的权威记录;`DECISIONS.md` D-021 与 `_sessions/2026-06-03-session-1.md` 有完整出处。
