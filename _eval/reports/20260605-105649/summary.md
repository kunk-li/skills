# Eval Summary · qwen

- Total tasks: 30
- PASS / WEAK / FAIL:  27 / 0 / 3
- Avg total score: 4.12 / 5.0

## By path

| path | runs | pass | avg |
|---|---|---|---|
| A | 10 | 9/10 | 4.17 |
| B | 13 | 11/13 | 3.91 |
| C | 7 | 7/7 | 4.43 |

## By level

| level | runs | pass | avg |
|---|---|---|---|
| L1 | 5 | 5/5 | 4.65 |
| L2 | 14 | 12/14 | 3.95 |
| L3 | 10 | 9/10 | 4.10 |
| L4 | 1 | 1/1 | 4.00 |

## By dimension (avg)

| dimension | runs | avg | min | runs<0.5 |
|---|---|---|---|---|
| selection | 30 | 0.90 | 0.00 | 3 |
| completeness | 30 | 0.90 | 0.00 | 3 |
| groundedness | 30 | 0.90 | 0.00 | 3 |
| format | 30 | 0.90 | 0.00 | 3 |
| gt_similarity | 30 | 0.52 | 0.00 | 7 |

## Per-task results

| id | path | L | verdict | sel | comp | gnd | fmt | util/gt | total |
|---|---|---|---|---|---|---|---|---|---|
| CINEMA-N070-business-rule-extraction | A | 3 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.6 | **4.6** |
| CINEMA-N070-data-object-identificati | A | 2 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.7 | **4.7** |
| CINEMA-N070-requirement-breakdown | A | 3 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.6 | **4.6** |
| CINEMA-N070-state-transition-mapping | A | 2 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.6 | **4.6** |
| CINEMA-N100-pending-items-extraction-rev5 | A | 1 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.6 | **4.6** |
| CINEMA-N100-requirement-completeness-rev5 | A | 1 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.7 | **4.7** |
| CINEMA-N100-requirement-conflict-det-rev5 | A | 1 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.6 | **4.6** |
| CINEMA-N100-requirement-executabilit-rev5 | A | 1 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.7 | **4.7** |
| CINEMA-N100-requirement-vulnerabilit-rev5 | A | 1 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.7 | **4.7** |
| CINEMA-N110-acceptance-criteria-gene | A | 2 | FAIL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | **0.0** |
| CINEMA-N120-api-design-recommendatio | B | 3 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.6 | **4.6** |
| CINEMA-N120-api-error-code-design | B | 2 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.7 | **4.7** |
| CINEMA-N120-api-intent-extraction | B | 2 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.7 | **4.7** |
| CINEMA-N120-audit-trail-design | B | 2 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.6 | **4.6** |
| CINEMA-N120-authorization-model-desi | B | 2 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.5 | **4.5** |
| CINEMA-N120-concurrency-control-reco | B | 3 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.6 | **4.6** |
| CINEMA-N120-data-flow-mapping | B | 3 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.7 | **4.7** |
| CINEMA-N120-engineering-requirement- | B | 3 | FAIL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | **0.0** |
| CINEMA-N120-idempotency-design-recom | B | 2 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.6 | **4.6** |
| CINEMA-N120-module-boundary-identifi | B | 2 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.7 | **4.7** |
| CINEMA-N120-performance-risk-analysi | B | 2 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.6 | **4.6** |
| CINEMA-N120-security-risk-analysis | B | 2 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.7 | **4.7** |
| CINEMA-N120-table-schema-design-reco | B | 2 | FAIL | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | **0.0** |
| CINEMA-N180-dependency-identificatio | C | 2 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.4 | **4.4** |
| CINEMA-N180-development-task-breakdo | C | 3 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.7 | **4.7** |
| CINEMA-N180-effort-estimation-assist | C | 2 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.7 | **4.7** |
| CINEMA-N190-code-scaffold-generation | C | 3 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.7 | **4.7** |
| CINEMA-N190-controller | C | 4 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | **4.0** |
| CINEMA-N190-transaction-boundary-che | C | 3 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.4 | **4.4** |
| CINEMA-N190-validator-code-generatio | C | 3 | PASS | 1.0 | 1.0 | 1.0 | 1.0 | 0.2 | **4.2** |