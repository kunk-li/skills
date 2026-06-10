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
| `mechanical` | 把已验证镜头编译成纯扫描器（authz_input / cleanup_coverage / contract_drift = 2 gate 判定逻辑 + 1 扩展） | ✅ 跑通，无需 key，产真数 |
| `llm` | 注入 SKILL.md 让模型找缺陷 + 不注入对照（delta=证 SKILL.md 真在提升检出非裸模型本能） | 🔶 接口就绪，接 `_eval/adapters.py` 的 run()，需 model endpoint |

## 现状 + 诚实读数
- 当前 6 fixture / 3 类全 recall=1.00 FP=0.00 —— 因为这 3 个 skill（016/017/093）**正是被真用打磨过的「验证脊」**，机械化后本就强。
- **关键诚实**（呼应 D-030）：harness 只能测**有 ground truth 的地方**，而 ground truth 只在**真用发生过**的地方存在 → 那 138 个 day-1 未碰 skill **没 fixture 可建**（没东西练过它们）。**S3 不逃 demand-pull，它把盲区从「不知道好不好」变成「可见地无信号、不可测」** —— 这本身就是「该不该优化它」的答案：不该,直到真用产出真缺陷。

## 扩展（按需，不 sweep）
1. 接 model endpoint 跑 `llm` 臂 → 出「带/不带 SKILL.md」delta（项目 env 现无 key）。
2. 新真缺陷出现时,把它蒸馏成通用 fixture 加进 `FIXTURES`（money_atomicity #33 / dead_code #37 需 call-graph/dataflow → 归 llm/审计臂,机械纯扫不准,见文件末注释）。
3. fixture 覆盖哪个 skill = 该 skill 被真用碰过的证据；fixture 数沿真用增长,不为覆盖率硬造。
