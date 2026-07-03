# desc-trim triggering benchmark · N300 高同族簇

> 目的:证「description 缩到 ≤25 词(去掉 NOT-for 路由提示)是否降低同族路由准确率」,
> 再决定是否批量对齐 139 个。用户 2026-07-03 选「先 benchmark 再批」。
> judge = Agent 子代理(不依赖 API key)。每 prompt 只给 5 个 name+description,选一个。

## 被测 5 同族(N300 运行监控与故障定位)

## PRE(原始长 description,含 NOT-for 路由提示)—— 见各 zip SKILL.md,词数 156/119/125/115/121

## POST(缩到 ≤25 词,gold 风格,去掉 Use-when 枚举 / NOT-for / Typical-triggers)

- **log-analysis** (21w): Investigate runtime logs to extract error signatures, correlate trace IDs, detect PII/secret exposure, and produce portable log queries for ops incidents.
- **monitoring-metric-interpretation** (25w): Interpret runtime metric anomalies — CPU, latency, traffic, error rate, saturation, SLO burn, business KPIs — during ops incidents, separating symptom from impact and computing burn rate.
- **trace-call-chain-analysis** (22w): Analyze distributed trace call chains to locate latency bottlenecks, error propagation paths, and span-level anomalies in production incidents, including end-to-end chain-completeness verification.
- **anomaly-clustering** (25w): Cluster raw anomalies from noisy logs, metrics, traces, and failed checks into deduplicated pattern groups with novelty flags and priority scores to accelerate incident diagnosis.
- **root-cause-analysis-recommendation** (25w): Chain evidence from logs, metrics, traces, anomaly clusters, and change records into ranked hypotheses and five-why reasoning to recommend the most probable incident root cause.

## 10 路由 prompt(每同族 2 个,含近邻边界情形;括号=ground truth)

1. (log-analysis) 40MB app.log from last night's outage — pull the top recurring error signatures and check whether any customer emails or API keys leaked into the log lines.
2. (log-analysis) Bundle of correlation-id'd logs for the checkout feature; we have NO tracing. Reconstruct whether the flow ran end-to-end and where it broke. [边界:vs trace]
3. (monitoring-metric-interpretation) Grafana shows CPU 95% and p99 latency doubled at 02:14 — is this the incident cause or a symptom, and how fast is our SLO error budget burning?
4. (monitoring-metric-interpretation) Error-rate metric jumped 0.1%→3% but last Tuesday's baseline was similar. Is this real signal or noise? [边界:vs anomaly-clustering]
5. (trace-call-chain-analysis) We have Jaeger traces for the slow requests — which span eats the p99, and where does the 500 originate as it propagates across services?
6. (trace-call-chain-analysis) First request after a deploy is always 8s then fine — using our trace data, find the cold-start/init delay. [边界:vs metric]
7. (anomaly-clustering) Thousands of raw alerts, log errors, failed healthchecks from the last hour — group the ones probably the same underlying issue and flag anything novel.
8. (anomaly-clustering) Dedupe these noisy signals across logs and metrics into pattern groups with a stable cluster id I can reference downstream. [边界:vs log-analysis]
9. (root-cause-analysis-recommendation) Given logs, metrics, traces, and the 02:00 deploy, rank the 2-3 most likely root causes with five-why reasoning. Regression or systemic?
10. (root-cause-analysis-recommendation) Chain all evidence into the most probable root cause of this incident — don't overstate certainty. [边界:vs anomaly/trace]

## 方法

- 6 个 judge 子代理:3 跑 PRE、3 跑 POST。每个独立看 5 个 name+description(对应条件)+ 全 10 prompt,逐条选一个 skill。
- 准确率 = 选中==ground truth 的比例。PRE 均值 vs POST 均值。
- 判据:POST ≥ PRE(在噪声内)→ 缩不掉路由 → 可批;POST 明显 < PRE → NOT-for 提示重要 → 别裸缩、需保留区分信号。
