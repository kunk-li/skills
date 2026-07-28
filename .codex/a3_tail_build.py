#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Codex-owned INTEG, FIND4, and BAR-EVAL artifacts for A3."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Any

CHAIN = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN")
INTEG = CHAIN / "INTEG"
FIND4 = CHAIN / "FIND4"
BAR_EVAL = CHAIN / "BAR-EVAL"
TODAY = datetime.now().strftime("%Y-%m-%d")

PHASE_EVIDENCE = [
    {
        "phase": "PARSE",
        "status": "done",
        "audit": "6/6",
        "evidence": "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/PARSE-FINDINGS.md",
        "total_input": "PRD slice and extracted requirement/rule/state/auth/data/audit signals.",
    },
    {
        "phase": "B-design",
        "status": "done",
        "audit": "19/19",
        "evidence": "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/B-design-FINDINGS.md",
        "total_input": "Architecture, authority decisions, risks, and cross-module design notes.",
    },
    {
        "phase": "C-task",
        "status": "done",
        "audit": "4/4",
        "evidence": "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/C-task/N180_planning_package.md",
        "total_input": "Task split and implementation planning package.",
    },
    {
        "phase": "D-code",
        "status": "done",
        "audit": "CODEX-A3-DCODE status=pass projects=2/2 java=210 surefire_tests=34",
        "evidence": "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/D-code/production-code/",
        "total_input": "Most-complete production implementation evidence; not a minimal kernel.",
    },
    {
        "phase": "TEST",
        "status": "done",
        "audit": "CODEX-A3-TEST status=pass targets=20/20",
        "evidence": "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/TEST/",
        "total_input": "Test strategy, cases, regression points, and risk checks.",
    },
    {
        "phase": "REL",
        "status": "done_no_go",
        "audit": "CODEX-A3-REL status=pass targets=11/11 csv_rows=50",
        "evidence": "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/REL/REL-COMPLETION-AUDIT.md",
        "total_input": "Release evidence inherits NO_GO because external decisions remain open.",
    },
    {
        "phase": "OPS",
        "status": "done_not_deployed",
        "audit": "CODEX-A3-OPS status=pass targets=14/14 csv_rows=4",
        "evidence": "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/OPS/OPS-COMPLETION-AUDIT.md",
        "total_input": "Operational docs only; no production deployment or telemetry.",
    },
    {
        "phase": "DOC",
        "status": "done_not_deployed",
        "audit": "CODEX-A3-DOC status=pass targets=18/18 csv_rows=23 workbook=present",
        "evidence": "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/DOC/DOC-COMPLETION-AUDIT.md",
        "total_input": "Documentation is complete as artifact set, but inherits release posture.",
    },
    {
        "phase": "CMP",
        "status": "done_evidence_only",
        "audit": "CODEX-A3-CMP status=pass targets=8/8 features=20 endpoints=261 generated_java=97 team_java=454 verdict=not_globally_generated_gte_team",
        "evidence": "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/CMP/CMP-SUMMARY.md",
        "total_input": "Generated-vs-team code comparison evidence; not the total verdict.",
    },
    {
        "phase": "PLAT",
        "status": "done",
        "audit": "CODEX-A3-PLAT status=pass targets=16/16 checks=36/36 csv_rows=60 markdown=6 yaml=present",
        "evidence": "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/PLAT/PLAT-COMPLETION-AUDIT.md",
        "total_input": "Platform/orchestration trace and phase control evidence.",
    },
]

OPEN_BLOCKERS = [
    {
        "id": "PEND-A3-02",
        "name": "72h physical reversal",
        "owner": "OA product/tech owner",
        "impact": "Blocks release posture and full bar1/bar2/bar5 acceptance.",
        "status": "open",
    },
    {
        "id": "PEND-A3-03",
        "name": "Large subtree strategy",
        "owner": "OA product/architecture owner",
        "impact": "Blocks full feature completeness and operational release confidence.",
        "status": "open",
    },
    {
        "id": "BRISK-002",
        "name": "hub-wflow saga compensation",
        "owner": "workflow/OA architecture owner",
        "impact": "Blocks full cross-module integration and conflict-resolution closure.",
        "status": "open",
    },
    {
        "id": "BRISK-006",
        "name": "E-table/v_d_table contract",
        "owner": "data/OA backend owner",
        "impact": "Blocks full data-contract integration and final business verification.",
        "status": "open",
    },
]

FIND4_CANDIDATES = [
    {
        "candidate_id": "CAND-A3-A1",
        "source": "A3 PARSE + F lineage",
        "finding": "Evidence anchor regex can break on dotted section numbers and non-atomic PRD IDs.",
        "class": "cross-module candidate",
        "fanout": "015 plus related evidence tools",
        "decision": "keep_candidate",
        "why": "Needs dedicated PRE<POST A/B before any library fold.",
    },
    {
        "candidate_id": "CAND-A3-A2",
        "source": "artifact_contract_check lineage",
        "finding": "workflow_alias and output aliases can be missed by older contract checks.",
        "class": "tooling candidate",
        "fanout": "contract checker and stage linkage tools",
        "decision": "keep_candidate",
        "why": "Already known family; fold only with isolated regression pack.",
    },
    {
        "candidate_id": "CAND-A3-A3",
        "source": "A3 017 template",
        "finding": "Template section 10 duplicate heading quality issue.",
        "class": "local template quality",
        "fanout": "017",
        "decision": "defer",
        "why": "Low blast radius; not enough evidence to fold during A3 closeout.",
    },
    {
        "candidate_id": "CAND-A3-B1",
        "source": "A3 graph/tree blind spot",
        "finding": "Graph/tree invariants are not first-class enough across rule/auth/API/schema skills.",
        "class": "possible library gap",
        "fanout": "013/014/016/024/036/037/038/041/046/049/052",
        "decision": "defer",
        "why": "n=1 for the new shape; requires more modules before fold.",
    },
    {
        "candidate_id": "CAND-A3-B2",
        "source": "A3 multi-status vocabulary",
        "finding": "Multiple state vocabularies require stronger alignment across design and docs.",
        "class": "possible library gap",
        "fanout": "state/design/doc skills",
        "decision": "defer",
        "why": "Needs cross-module confirmation and an A/B acceptance metric.",
    },
    {
        "candidate_id": "CAND-A3-B3",
        "source": "supersede lineage",
        "finding": "Supersede/deprecated-node lineage remains a recurring risk family.",
        "class": "known family",
        "fanout": "requirements, state, release, ops",
        "decision": "keep_candidate",
        "why": "Do not fold again without proving PRE<POST improvement on current chain.",
    },
    {
        "candidate_id": "CAND-A3-B4",
        "source": "A3 ReBAC tree scope",
        "finding": "Tree-scope delegated authorization needs stronger expression and verification.",
        "class": "possible library gap",
        "fanout": "016 plus auth/design/test skills",
        "decision": "defer",
        "why": "Important but still needs sibling-module evidence.",
    },
    {
        "candidate_id": "CAND-A3-CMP-01",
        "source": "CMP repair",
        "finding": "HC occupied-usage formula and org-change lock semantics needed generated-code repair.",
        "class": "implementation repair, not skill fold",
        "fanout": "D-code implementation",
        "decision": "do_not_fold_now",
        "why": "Repair landed in generated code; no isolated skill A/B was run.",
    },
]

BAR_SCORECARD = [
    {
        "number": 1,
        "id": "bar1",
        "name": "PRD-to-code complete coverage",
        "status": "PARTIAL",
        "score": 0.5,
        "basis": "D-code covers the A3 core slices and CMP confirms meaningful generated coverage, but CMP did not prove generated >= team globally and external release decisions remain open.",
        "evidence": [
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/D-code/production-code/",
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/CMP/FEATURE-CMP-MATRIX.csv",
        ],
        "blocking_facts": ["PEND-A3-02", "PEND-A3-03", "CMP verdict=not_globally_generated_gte_team"],
    },
    {
        "number": 2,
        "id": "bar2",
        "name": "Feature completeness",
        "status": "PARTIAL",
        "score": 0.5,
        "basis": "Feature artifacts and code are substantive, but team code remains broader in production integration, hub-wflow, scheduled lock reconciliation, dispatch/deployment/workbench breadth.",
        "evidence": [
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/CMP/CMP-SUMMARY.md",
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/INTEG/INTEG-EVIDENCE-MATRIX.csv",
        ],
        "blocking_facts": ["BRISK-002", "BRISK-006"],
    },
    {
        "number": 3,
        "id": "bar3",
        "name": "No vulnerabilities",
        "status": "PARTIAL",
        "score": 0.5,
        "basis": "Known CMP-exposed HC and lock gaps were repaired, Maven tests pass, and no-stub scan is clean; this is still not equivalent to a full production security proof.",
        "evidence": [
            "CODEX-A3-DCODE status=pass projects=2/2 java=210 surefire_tests=34",
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/CMP/OBSERVATION-FOR-OA-VERIFY.md",
        ],
        "blocking_facts": ["No deployed production telemetry", "external integration not fully verified"],
    },
    {
        "number": 4,
        "id": "bar4",
        "name": "Tests cover all business behavior",
        "status": "PARTIAL",
        "score": 0.5,
        "basis": "A3 has 20/20 test artifacts and 34 Surefire tests, but full business coverage against the broader production integration surface is not proven.",
        "evidence": [
            "CODEX-A3-TEST status=pass targets=20/20",
            "CODEX-A3-DCODE status=pass projects=2/2 java=210 surefire_tests=34",
        ],
        "blocking_facts": ["Team production breadth not fully mirrored", "external contracts open"],
    },
    {
        "number": 5,
        "id": "bar5",
        "name": "PRD defects have replacement implementation",
        "status": "PARTIAL",
        "score": 0.5,
        "basis": "A3 records decision gaps and implements safe fallback posture, but external decisions such as 72h reversal, large subtree strategy, hub-wflow saga, and E-table contracts are not fully replaced by accepted implementation.",
        "evidence": [
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/REL/REL-COMPLETION-AUDIT.md",
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/PLAT/PLAT-COMPLETION-AUDIT.md",
        ],
        "blocking_facts": ["PEND-A3-02", "PEND-A3-03", "BRISK-002", "BRISK-006"],
    },
    {
        "number": 6,
        "id": "bar6",
        "name": "Identify unreasonable PRD points",
        "status": "PASS",
        "score": 1.0,
        "basis": "PARSE and B-design independently surfaced tree-depth ambiguity, state-vocabulary drift, supersede dead-branch retention, scope definition gaps, and external-decision gaps.",
        "evidence": [
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/PARSE-FINDINGS.md",
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/B-design-FINDINGS.md",
        ],
        "blocking_facts": [],
    },
    {
        "number": 7,
        "id": "bar7",
        "name": "Cross-module conflicts identified and solved",
        "status": "PARTIAL",
        "score": 0.5,
        "basis": "Cross-module conflicts were identified, but hub-wflow saga compensation and E-table/v_d_table contract closure still require external owners.",
        "evidence": [
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/INTEG/INTEG-BLOCKER-ALIGNMENT.md",
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/FIND4/FIND4-CANDIDATE-TRIAGE.csv",
        ],
        "blocking_facts": ["BRISK-002", "BRISK-006"],
    },
    {
        "number": 8,
        "id": "bar8",
        "name": "Lowest iteration count",
        "status": "PARTIAL",
        "score": 0.5,
        "basis": "The code path was made runnable and CMP repairs landed in the follow-up, but A3 required multiple corrective loops and does not prove minimum iteration.",
        "evidence": [
            "D:/work/资料/skills/_sessions/2026-07-27-session-16.md",
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/CMP/OBSERVATION-FOR-OA-VERIFY.md",
        ],
        "blocking_facts": ["Corrective loops after user challenge", "CMP repair loop required"],
    },
    {
        "number": 9,
        "id": "bar9",
        "name": "Quality review is comprehensive",
        "status": "PASS",
        "score": 1.0,
        "basis": "A3 has explicit audits across D-code, TEST, REL, OPS, DOC, CMP, PLAT, INTEG, FIND4, and BAR-EVAL; CMP found real internal gaps and the follow-up repaired them.",
        "evidence": [
            "D:/work/资料/skills/.codex/oa_shakedown.py",
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/CMP/CMP-COMPLETION-AUDIT.md",
        ],
        "blocking_facts": [],
    },
    {
        "number": 10,
        "id": "bar10",
        "name": "Architecture optimization",
        "status": "PARTIAL",
        "score": 0.5,
        "basis": "Generated code is stronger on tree_path boundary safety and A3-local J1 hash-chain, but production-breadth integration and external architecture choices remain incomplete.",
        "evidence": [
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/CMP/CMP-SUMMARY.md",
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/D-code/production-code/",
        ],
        "blocking_facts": ["production integration breadth not matched", "external architecture decisions open"],
    },
    {
        "number": 11,
        "id": "bar11",
        "name": "Less code with better implementation",
        "status": "FAIL",
        "score": 0.0,
        "basis": "Generated code is smaller in local metrics, but function-equivalence and production-breadth equivalence to the team implementation are not proven; therefore 'less and better' cannot pass.",
        "evidence": [
            "D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN/CMP/CMP-SUMMARY.md",
            "CMP generated_java=97 team_java=454 verdict=not_globally_generated_gte_team",
        ],
        "blocking_facts": ["function equivalence not proven", "team code broader"],
    },
]


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, str]], header: list[str], comments: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        for comment in comments or []:
            fh.write(f"# {comment}\n")
        writer = csv.DictWriter(fh, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def md_header(artifact_name: str, artifact_type: str, producer: str, phase: str) -> str:
    return dedent(
        f"""
        ---
        artifact_contract:
          schema_version: a3.tail.artifact.v1
          artifact_name: {artifact_name}
          artifact_type: {artifact_type}
          producer_skill: {producer}
          producer_node: {phase}
          module: A3-org
          chain_root: D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN
          readiness: pass
        self_gate:
          status: pass
          failed_rules: []
        ---
        """
    ).strip()


def build_integ() -> None:
    evidence_rows = [
        {
            "phase": item["phase"],
            "status": item["status"],
            "audit": item["audit"],
            "evidence": item["evidence"],
            "bar_eval_input": item["total_input"],
        }
        for item in PHASE_EVIDENCE
    ]
    write_csv(
        INTEG / "INTEG-EVIDENCE-MATRIX.csv",
        evidence_rows,
        ["phase", "status", "audit", "evidence", "bar_eval_input"],
        [
            "producer_skill: integration-evidence-reconciliation",
            "workflow_node: INTEG",
            "node_artifact_target: INTEG-EVIDENCE-MATRIX.csv",
        ],
    )

    continuity = []
    for idx, item in enumerate(PHASE_EVIDENCE):
        continuity.append(
            {
                "seq": str(idx + 1),
                "phase": item["phase"],
                "input_from_previous": "root input" if idx == 0 else PHASE_EVIDENCE[idx - 1]["phase"],
                "output_to_next": "BAR-EVAL input" if idx == len(PHASE_EVIDENCE) - 1 else PHASE_EVIDENCE[idx + 1]["phase"],
                "continuity_status": "connected",
                "notes": item["audit"],
            }
        )
    continuity.extend(
        [
            {
                "seq": "11",
                "phase": "INTEG",
                "input_from_previous": "PLAT",
                "output_to_next": "FIND4",
                "continuity_status": "connected",
                "notes": "Integration reconciles phase evidence and open external blockers.",
            },
            {
                "seq": "12",
                "phase": "FIND4",
                "input_from_previous": "INTEG",
                "output_to_next": "BAR-EVAL",
                "continuity_status": "connected",
                "notes": "Candidate gaps are triaged; no skill fold without PRE<POST A/B.",
            },
            {
                "seq": "13",
                "phase": "BAR-EVAL",
                "input_from_previous": "FIND4",
                "output_to_next": "total verdict",
                "continuity_status": "connected",
                "notes": "Only all 11 bars PASS can produce PASS; otherwise final state is NO_GO.",
            },
        ]
    )
    write_csv(
        INTEG / "INTEG-PHASE-CONTINUITY.csv",
        continuity,
        ["seq", "phase", "input_from_previous", "output_to_next", "continuity_status", "notes"],
        [
            "producer_skill: phase-continuity-check",
            "workflow_node: INTEG",
            "node_artifact_target: INTEG-PHASE-CONTINUITY.csv",
        ],
    )

    blocker_lines = [
        md_header("INTEG-BLOCKER-ALIGNMENT.md", "integration_blocker_alignment", "integration-evidence-reconciliation", "INTEG"),
        "",
        "# A3 INTEG Blocker Alignment",
        "",
        "INTEG result: phase evidence is connected, but the total judgment remains blocked until BAR-EVAL scores the 11 bars.",
        "",
        "CMP is evidence only. It does not replace BAR-EVAL and does not prove generated code is globally greater than or equal to team code.",
        "",
        "## Open External Blockers",
        "",
    ]
    for blocker in OPEN_BLOCKERS:
        blocker_lines.append(f"- {blocker['id']}: {blocker['name']}. Owner: {blocker['owner']}. Impact: {blocker['impact']}")
    blocker_lines.extend(
        [
            "",
            "## Integration Judgment",
            "",
            "The chain is integrated enough to enter FIND4 and BAR-EVAL. It is not integrated enough to claim production release or 11-bar pass.",
        ]
    )
    write_text(INTEG / "INTEG-BLOCKER-ALIGNMENT.md", "\n".join(blocker_lines))

    write_text(
        INTEG / "INTEG-TOTAL-JUDGMENT-INPUT.md",
        md_header("INTEG-TOTAL-JUDGMENT-INPUT.md", "total_judgment_input_package", "integration-evidence-reconciliation", "INTEG")
        + dedent(
            """

            # A3 INTEG Total Judgment Input Package

            This file is the handoff from INTEG to FIND4 and BAR-EVAL.

            Confirmed evidence:

            - D-code audit passed with two Maven projects, 210 Java files, and 34 Surefire tests.
            - TEST, REL, OPS, DOC, CMP, and PLAT artifact audits passed.
            - CMP verdict is not globally generated>=team. Generated code is stronger on tree_path boundary safety and A3-local J1 hash-chain; team code remains broader in production integration.
            - Four external blockers remain open: PEND-A3-02, PEND-A3-03, BRISK-002, BRISK-006.

            Total-judgment rule:

            - BAR-EVAL must score all 11 D-060 acceptance bars as PASS.
            - If any bar is PARTIAL or FAIL after all phases are complete, the module final computed_total is NO_GO.
            """
        ),
    )

    write_text(
        INTEG / "INTEG-COMPLETION-AUDIT.md",
        md_header("INTEG-COMPLETION-AUDIT.md", "completion_audit", "codex-integ-completion-audit", "INTEG")
        + dedent(
            """

            # A3 INTEG Completion Audit

            INTEG is complete as an integration-evidence reconciliation stage.

            Completed inputs:

            - PARSE, B-design, C-task, D-code, TEST, REL, OPS, DOC, CMP, and PLAT are connected.
            - Evidence matrix, continuity matrix, blocker alignment, and total-judgment input package are present.

            Boundary:

            - INTEG does not decide A3 pass/fail.
            - INTEG confirms the chain is ready for FIND4 and BAR-EVAL.
            - Release posture remains NO_GO / NOT_DEPLOYED.
            """
        ),
    )

    write_json(
        INTEG / "INTEG-ARTIFACT-MANIFEST.json",
        {
            "schema_version": "a3.integ.manifest.v1",
            "module": "A3-org",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "artifacts": sorted(p.name for p in INTEG.iterdir() if p.is_file()),
            "result": "complete",
            "next": "FIND4",
            "total_verdict": "NOT_DONE",
            "open_blockers": [item["id"] for item in OPEN_BLOCKERS],
        },
    )


def build_find4() -> None:
    write_csv(
        FIND4 / "FIND4-CANDIDATE-TRIAGE.csv",
        FIND4_CANDIDATES,
        ["candidate_id", "source", "finding", "class", "fanout", "decision", "why"],
        [
            "producer_skill: defect-fanout-triage",
            "workflow_node: FIND4",
            "node_artifact_target: FIND4-CANDIDATE-TRIAGE.csv",
        ],
    )

    ab_rows = []
    for item in FIND4_CANDIDATES:
        ab_rows.append(
            {
                "candidate_id": item["candidate_id"],
                "pre_post_ab_run": "no",
                "library_fold": "no",
                "library_count_after": "157",
                "reason": item["why"],
            }
        )
    write_csv(
        FIND4 / "FIND4-FANOUT-AB-DECISION.csv",
        ab_rows,
        ["candidate_id", "pre_post_ab_run", "library_fold", "library_count_after", "reason"],
        [
            "producer_skill: fanout-ab-decision",
            "workflow_node: FIND4",
            "node_artifact_target: FIND4-FANOUT-AB-DECISION.csv",
        ],
    )

    write_text(
        FIND4 / "FIND4-LIBRARY-FOLD-RECOMMENDATION.md",
        md_header("FIND4-LIBRARY-FOLD-RECOMMENDATION.md", "library_fold_recommendation", "defect-fanout-triage", "FIND4")
        + dedent(
            """

            # A3 FIND4 Library Fold Recommendation

            FIND4 result: no skill-library fold is recommended in this A3 closeout.

            Reason:

            - Several candidates are real enough to keep in the fan-out ledger.
            - None of them received an isolated PRE<POST A/B proof during this tail closeout.
            - The library count therefore remains 157.

            Follow-up shape:

            - CAND-A3-A1 and CAND-A3-A2 should be handled in a later dedicated contract/evidence tooling A/B pass.
            - B1/B2/B3/B4 need more module evidence before folding broad library behavior.
            - CMP HC/lock findings were implementation repairs and should not be retroactively called a skill fold.
            """
        ),
    )

    write_text(
        FIND4 / "FIND4-COMPLETION-AUDIT.md",
        md_header("FIND4-COMPLETION-AUDIT.md", "completion_audit", "codex-find4-completion-audit", "FIND4")
        + dedent(
            """

            # A3 FIND4 Completion Audit

            FIND4 is complete as a candidate-gap fan-out and fold decision stage.

            Result:

            - Candidates triaged: 8.
            - Library folds performed: 0.
            - Library count remains: 157.
            - Next phase: BAR-EVAL.

            Boundary:

            - FIND4 does not decide A3 pass/fail.
            - No candidate can be called folded without PRE<POST A/B evidence.
            """
        ),
    )

    write_json(
        FIND4 / "FIND4-ARTIFACT-MANIFEST.json",
        {
            "schema_version": "a3.find4.manifest.v1",
            "module": "A3-org",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "artifacts": sorted(p.name for p in FIND4.iterdir() if p.is_file()),
            "result": "complete",
            "next": "BAR-EVAL",
            "candidate_count": len(FIND4_CANDIDATES),
            "library_folds": 0,
            "library_count": 157,
        },
    )


def build_bar_eval() -> None:
    pass_count = sum(1 for item in BAR_SCORECARD if item["status"] == "PASS")
    partial_count = sum(1 for item in BAR_SCORECARD if item["status"] == "PARTIAL")
    fail_count = sum(1 for item in BAR_SCORECARD if item["status"] == "FAIL")
    total_score = sum(float(item["score"]) for item in BAR_SCORECARD)
    all_pass = pass_count == 11 and partial_count == 0 and fail_count == 0
    verdict = "PASS" if all_pass else "NO_GO"

    scorecard = {
        "schema_version": "a3.bar_eval.scorecard.v1",
        "module": "A3-org",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "strict_rule": "A3 passes only if all 11 D-060 acceptance bars are PASS.",
        "total_verdict": verdict,
        "computed_total_expected": verdict,
        "all_pass": all_pass,
        "summary": {
            "pass": pass_count,
            "partial": partial_count,
            "fail": fail_count,
            "bars_total": len(BAR_SCORECARD),
            "numeric_score": total_score,
            "numeric_score_max": 11,
        },
        "bars": BAR_SCORECARD,
    }
    write_json(BAR_EVAL / "BAR-EVAL-11BAR-SCORECARD.json", scorecard)

    lines = [
        md_header("BAR-EVAL-11BAR-SCORECARD.md", "11_bar_scorecard", "bar-eval-total-judgment", "BAR-EVAL"),
        "",
        "# A3 BAR-EVAL 11-Bar Scorecard",
        "",
        f"Date: {TODAY}",
        "",
        f"Total verdict: {verdict}",
        "",
        f"Score summary: {pass_count} PASS, {partial_count} PARTIAL, {fail_count} FAIL, out of 11 bars.",
        "",
        "Rule: A3 passes only if all 11 D-060 acceptance bars are PASS. CMP is code-comparison evidence only.",
        "",
        "## Bar Results",
        "",
    ]
    for item in BAR_SCORECARD:
        lines.extend(
            [
                f"### bar{item['number']} - {item['name']}",
                "",
                f"- Status: {item['status']}",
                f"- Basis: {item['basis']}",
                f"- Blocking facts: {', '.join(item['blocking_facts']) if item['blocking_facts'] else '-'}",
                "",
            ]
        )
    write_text(BAR_EVAL / "BAR-EVAL-11BAR-SCORECARD.md", "\n".join(lines))

    write_text(
        BAR_EVAL / "BAR-EVAL-COMPLETION-AUDIT.md",
        md_header("BAR-EVAL-COMPLETION-AUDIT.md", "completion_audit", "codex-bar-eval-completion-audit", "BAR-EVAL")
        + dedent(
            f"""

            # A3 BAR-EVAL Completion Audit

            BAR-EVAL is complete.

            Result:

            - Bars scored: 11/11.
            - PASS: {pass_count}.
            - PARTIAL: {partial_count}.
            - FAIL: {fail_count}.
            - Total verdict: {verdict}.

            Meaning:

            - A3 is fully run through the remaining tail stages.
            - A3 does not pass the 11-bar acceptance bar.
            - Final computed_total must be NO_GO, not PASS and not NOT_DONE.
            """
        ),
    )

    write_json(
        BAR_EVAL / "BAR-EVAL-ARTIFACT-MANIFEST.json",
        {
            "schema_version": "a3.bar_eval.manifest.v1",
            "module": "A3-org",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "artifacts": sorted(p.name for p in BAR_EVAL.iterdir() if p.is_file()),
            "result": "complete",
            "total_verdict": verdict,
            "score_summary": scorecard["summary"],
        },
    )


def build() -> None:
    INTEG.mkdir(parents=True, exist_ok=True)
    FIND4.mkdir(parents=True, exist_ok=True)
    BAR_EVAL.mkdir(parents=True, exist_ok=True)
    build_integ()
    build_find4()
    build_bar_eval()


if __name__ == "__main__":
    build()
    print(f"Generated A3 tail artifacts under {CHAIN}")
