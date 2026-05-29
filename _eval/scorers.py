"""Five scoring dimensions for the eval suite.

Each scorer returns a float in [0, 1]. The eval framework sums them
into a total in [0, 5]. Thresholds: total>=4 PASS, 3-4 WEAK, <3 FAIL.

selection    — did the agent pick the right (macro/atomic) skill?
completeness — does the response contain required artifacts/sections?
groundedness — did the agent stay grounded (no fabrication)?
format       — schema/structure validity of the response.
utility      — would a human reviewer call it usable?
"""

import json
import re

DIMENSIONS = ["selection", "completeness", "groundedness", "format", "utility"]

# Ground-truth eval adds a 6th dimension (only used when task has
# expected.ground_truth_path). The total stays comparable by scaling
# the regular 5-dim total: when ground_truth is present, we drop the
# utility judge (now subsumed by gt_similarity) and add gt_similarity.
GROUND_TRUTH_DIMENSIONS = ["selection", "completeness", "groundedness", "format", "gt_similarity"]


def score_selection(task, response):
    """1 if expected skill was selected (or correctly skipped for L5).

    Task `expected.macro_skill` is the expected skill name. If
    `expected.must_not_call` is set (L5 adversarial), the expected
    skill must NOT be in the response.
    """
    expected = task["expected"]
    selected = set(response.get("selected_skills") or [])
    must_not = expected.get("must_not_call")
    if must_not:
        return 0.0 if must_not in selected else 1.0
    target = expected.get("macro_skill") or expected.get("atomic_skill")
    if not target:
        return 1.0
    if target in selected:
        return 1.0
    # Partial credit if a near-cousin atomic skill was called
    cousins = expected.get("near_cousins", [])
    if any(c in selected for c in cousins):
        return 0.5
    return 0.0


def score_completeness(task, response):
    """Fraction of required artifacts present, with all-or-nothing kicker.

    `expected.required_artifacts` is a list of filenames.
    """
    required = task["expected"].get("required_artifacts") or []
    if not required:
        return 1.0
    artifacts = response.get("artifacts") or {}
    present = sum(1 for r in required if r in artifacts)
    ratio = present / len(required)
    if ratio >= 0.95:
        return 1.0
    if ratio >= 0.6:
        return 0.6
    if ratio >= 0.3:
        return 0.3
    return 0.0


def score_groundedness(task, response, adapter):
    """LLM-as-judge: did the response fabricate facts not in the input?

    Falls back to a deterministic heuristic if adapter doesn't support
    judging (e.g. mock).
    """
    artifacts = response.get("artifacts") or {}
    # Compact joined artifact text
    blob = "\n\n".join(str(v) for v in artifacts.values())[:8000]
    if not blob.strip():
        return 0.0
    judge_prompt = f"""You are evaluating whether the agent response below is grounded
in the user input. The agent must distinguish CONFIRMED FACTS, REASONABLE
ASSUMPTIONS, and OPEN QUESTIONS — assumptions are OK if labeled.

User input:
{task['input']}

Agent response (excerpts):
{blob}

Question: Does the response present unsupported claims as facts (e.g. invented
users, fabricated requirements, made-up technical limits, fake metrics) WITHOUT
labeling them as assumptions?

Reply with a single number:
- 1.0 = grounded; assumptions are labeled
- 0.5 = some claims unclear or ambiguously labeled
- 0.0 = significant fabrication presented as fact
"""
    return adapter.judge(judge_prompt)


def score_format(task, response):
    """Schema sanity: artifacts dict-shaped, no obviously broken keys.

    Optional: task can include `expected.format_checks` for stricter rules.
    """
    if "error" in response:
        return 0.0
    artifacts = response.get("artifacts")
    if not isinstance(artifacts, dict):
        return 0.0
    if not artifacts:
        return 0.0
    # All values should be string-like (markdown / yaml / json text)
    for k, v in artifacts.items():
        if not isinstance(v, (str, dict, list)):
            return 0.3

    # Task-level explicit checks
    checks = task["expected"].get("format_checks") or []
    if not checks:
        return 1.0

    passed = 0
    for check in checks:
        kind = check.get("kind")
        if kind == "section_count":
            doc = artifacts.get(check["file"], "")
            sections = re.findall(r"^##\s+", doc, re.MULTILINE)
            expected_n = check["count"]
            if abs(len(sections) - expected_n) <= 1:
                passed += 1
        elif kind == "contains":
            doc = artifacts.get(check["file"], "")
            if check["text"] in doc:
                passed += 1
        elif kind == "min_length":
            doc = artifacts.get(check["file"], "")
            if len(doc) >= check["min"]:
                passed += 1
    return passed / len(checks)


def score_utility(task, response, adapter):
    """LLM-as-judge: would a human reviewer find this usable?"""
    artifacts = response.get("artifacts") or {}
    blob = "\n\n".join(str(v) for v in artifacts.values())[:8000]
    if not blob.strip():
        return 0.0
    judge_prompt = f"""Rate the practical usefulness of this agent response 0.0-1.0.

User asked: {task['input']}

Agent produced:
{blob}

Imagine you are a senior engineer or PM receiving this response. Rate:
- 1.0 = usable as-is or with minor edits (< 1 hour rework)
- 0.7 = directionally right, needs moderate edits (a few hours)
- 0.4 = some useful parts, but mostly needs rewrite
- 0.0 = would throw away and start over

Reply with a single number between 0.0 and 1.0.
"""
    return adapter.judge(judge_prompt)


def score_gt_similarity(task, response, adapter):
    """Ground-truth dimension: compare agent output to the real human artifact.

    Active when task.expected.ground_truth_path points at a real file
    (e.g. CinemaAI artifacts). LLM-as-judge does semantic + structural
    comparison. Returns 0.0-1.0.
    """
    import os
    gt_path = task["expected"].get("ground_truth_path")
    if not gt_path or not os.path.exists(gt_path):
        return 1.0  # no GT → don't penalize
    try:
        with open(gt_path, encoding="utf-8") as f:
            gt = f.read()[:12000]  # cap to keep judge prompt reasonable
    except Exception:
        return 0.5
    artifacts = response.get("artifacts") or {}
    agent_blob = "\n\n".join(str(v) for v in artifacts.values())[:12000]
    if not agent_blob.strip():
        return 0.0

    judge_prompt = f"""You are comparing an agent's output to a ground-truth artifact
produced by a senior PM/engineer team.

User asked the agent: {task['input']}

GROUND TRUTH (human-vetted):
{gt}

AGENT OUTPUT:
{agent_blob}

Rate the agent's output 0.0-1.0 against ground truth across:
- coverage: how many key sections/items/findings in GT are also in agent output?
- correctness: does agent's content align with GT's claims?
- additional value: anything in agent output that's worth keeping even if not in GT? (slight bonus)
- harmful extras: fabricated claims absent from GT or contradicting it? (penalty)

Scale:
- 1.0 = covers GT thoroughly, no fabrication, could substitute for GT
- 0.7 = covers main points, missing some details, no harmful fabrication
- 0.4 = covers some points, missing many, possibly some hallucination
- 0.0 = mostly off-topic, fabricated, or empty

Reply with ONLY a single number 0.0-1.0.
"""
    return adapter.judge(judge_prompt)


def score_response(task, response, adapter):
    """Run all scorers; return dict keyed by dimension.

    If task has ground_truth_path, use GROUND_TRUTH_DIMENSIONS;
    otherwise use the default 5 (with utility).
    """
    has_gt = bool(task.get("expected", {}).get("ground_truth_path"))
    scores = {
        "selection": score_selection(task, response),
        "completeness": score_completeness(task, response),
        "groundedness": score_groundedness(task, response, adapter),
        "format": score_format(task, response),
    }
    if has_gt:
        scores["gt_similarity"] = score_gt_similarity(task, response, adapter)
    else:
        scores["utility"] = score_utility(task, response, adapter)
    return scores
