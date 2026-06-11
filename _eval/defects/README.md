# S3 · 缺陷检测 eval（measurement 引擎）

> D-030 定的「长久优化流程」唯一缺环。现有 `_eval`（产物相似度，4 维饱和 0.90 + gt_similarity 混 D-012 偏差）**分不出强弱 skill**；本 harness 补上「skill 套真码能不能抓到已知缺陷」这一维——D-016/D-018 全部价值所在。

## 怎么跑
```
python _eval/defects/defect_eval.py
```
零三方依赖、**机械臂无需 API key**，直接产 per-skill recall/FP 排序 + scorer 自检。

## 设计要点
- **机械判据规避 D-012**：检出 = report 行号命中 ground-truth `defect_line`（行匹配），不靠 LLM 比相似度 → 与被测模型无关（不受「GT 是 Claude、被测是 qwen」偏差）。
- **干净码负样本测 FP**：每个 fixture 配 `clean` 变体；强 skill = 高 recall + 低 FP，弱 = 漏或滥报。
- **per-skill 排序**：fixture 标 `defect_class → skill`，聚合「哪个 skill 在哪类缺陷上弱」= **该优化谁**。
- **fixture = 通用缺陷类最小复现**（D-023，不复制项目专有码）；真码侧检出力由 2 个 gate 已在 dream_true 289 文件 / 真 P0 行验过（`skill-strengthening/06,07-demo-*.md`，在 skills-pilot）。`provenance` 把每类追到真实缺陷事件。

## 两个 detector 臂
| 臂 | 是什么 | 状态 |
|---|---|---|
| `mechanical` | 把镜头编译成纯扫描器（authz_input / cleanup_coverage / contract_drift / audit_coverage = 已折镜头;disabled_guard = NEW-1 蒸馏的 fold-candidate） | ✅ 跑通，无需 key，产真数 |
| `llm` | 注入 SKILL.md 让模型找缺陷 + 不注入对照（delta=证 SKILL.md 真在提升检出非裸模型本能） | 🔶 接口就绪，接 `_eval/adapters.py` 的 run()，需 model endpoint |

## 现状 + 诚实读数
- 当前 10 fixture / 5 类。4 类(016/017/093/054)recall=1.00 FP=0.00 = 镜头**已折进 skill**，S3 确认其有效（这几个 skill 正是被真用打磨过的「验证脊」）。第 5 类 `disabled_guard` 也 recall=1.00 FP=0.00，但镜头**尚未折进 070** → S3 在此扮演**标缺口**而非确认强:recall 测的是 detector 可机械化、不是 070 现状。输出里 `⟨lens 已折⟩` vs `⟨lens 待折=fold-candidate⟩` 把两者区分开，防误读。
- **OA(Java)第二域扩源**（2026-06-11）：`audit_coverage` 类(054 Audit-coverage 镜头)蒸馏自 OA master-audit operator 核过的 C4(免密复活零审计)/H7(grantRole 等家族零审计)，当天复核于 `origin/master@b31523b9` 再次确认 still_open。配 Python + Java 双形态 fixture，detector 同时认 `def` / 修饰符方法头 + `@AuditLog` 注解 = S3 首个非 Python fixture，缺陷类语言无关。**诚实**：OA 12 条里只有 audit_coverage 能干净机械化；其余 9 条(双签 quorum 死码 / 无锁并发 / 跨服务端点缺失 / 读不存在字段 / 撞唯一键 / 词表错配)需跨文件或 dataflow，留 llm/审计臂（见 `defect_eval.py` 末注释）。
- **NEW-1 增量缺陷蒸馏 → `disabled_guard` 类(fold-candidate)**（2026-06-11）：D-031 循环第二次复核抓到「他人当日引入的新缺陷」—— USDT 封板期合规守卫被自带「勿提交」标记的临时旁路注释掉、却 merge 进 release 线(operator 核过)。蒸馏成双信号共现 detector(旁路标记 + 邻近被注释的 throw/raise)，Python + Java 双形态。**镜头未折进 070**(070 现有「Dead guard」是结构性死守卫、未覆盖「被注释的活守卫」)→ 标 `lens_status=candidate`，下轮 D-019 fold 候选。= **S3 的「标缺口」价值首次真用**：一条真缺陷出现 → 可机械测 → 但现有 skill 抓不到 → 指出该折哪（D-030 的核心产物「该优化谁」)。
- **关键诚实**（呼应 D-030）：harness 只能测**有 ground truth 的地方**，而 ground truth 只在**真用发生过**的地方存在 → 那 138 个 day-1 未碰 skill **没 fixture 可建**（没东西练过它们）。**S3 不逃 demand-pull，它把盲区从「不知道好不好」变成「可见地无信号、不可测」** —— 这本身就是「该不该优化它」的答案：不该,直到真用产出真缺陷。**054 现有 fixture = 它被 OA 真用碰过的证据**（沿真用增长,不为覆盖率硬造）。

## 扩展（按需，不 sweep）
1. 接 model endpoint 跑 `llm` 臂 → 出「带/不带 SKILL.md」delta（项目 env 现无 key）。
2. 新真缺陷出现时,把它蒸馏成通用 fixture 加进 `FIXTURES`（money_atomicity #33 / dead_code #37 需 call-graph/dataflow → 归 llm/审计臂,机械纯扫不准,见文件末注释）。
3. fixture 覆盖哪个 skill = 该 skill 被真用碰过的证据；fixture 数沿真用增长,不为覆盖率硬造。
