"""Build a ground-truth eval task set from real CinemaAI artifacts.

This treats the 41 工件 under cinemaai/CinemaAI-PRD/工作产物/ as a
gold standard. Each artifact becomes one eval task:

    input        = "Given PRD v0.4 + sibling artifacts, produce a
                    {producer_skill} artifact for {workflow_node}."
    expected     = the real artifact file (used as ground truth for
                    structural and semantic comparison)
    skill        = producer_skill from artifact YAML frontmatter

Usage:
    python cinemaai_eval_builder.py
        --root  D:/projects/python/ai_work/video/cinemaai/CinemaAI-PRD
        --out   tasks_cinemaai.yaml

Output: a tasks_cinemaai.yaml that's loadable by eval.py just like
tasks.yaml — but each task points at a ground-truth file under
expected.ground_truth_path so the ground_truth_similarity scorer
can run.
"""

import argparse
import os
import re
from pathlib import Path

import yaml


# CSV files don't have YAML frontmatter; map filename -> producer_skill manually.
# Source: cinemaai/CinemaAI-PRD/工作产物/INDEX.md "二、按节点" section.
CSV_TO_SKILL = {
    # N070
    "业务规则清单.csv": "business-rule-extraction",
    "状态流转表.csv": "state-transition-mapping",
    "数据对象清单.csv": "data-object-identification",
    # N100 (each skill emits both .csv + 摘要.md)
    "完整性检查单.csv": "requirement-completeness-check",
    "可执行性检查单.csv": "requirement-executability-check",
    "需求矛盾问题单.csv": "requirement-conflict-detection",
    "需求漏洞清单.csv": "requirement-vulnerability-scan",
    "待确认项清单.csv": "pending-items-extraction",
    # N110
    "验收标准.csv": "acceptance-criteria-generation",
    # N120
    "API意图清单.csv": "api-intent-extraction",
    # N180
    "开发任务清单.csv": "development-task-breakdown",
}

# Map node id -> eval "path" letter (matches our 5-path taxonomy)
NODE_TO_PATH = {
    "N070": "A",   # requirement structuring (path A's middle step)
    "N100": "A",   # PRD quality gate (path A's later step)
    "N110": "A",   # handover
    "N120": "B",   # tech solution + API + schema (path B core)
    "N180": "C",   # dev tasks
    "N190": "C",   # scaffold (could be D but is pre-coding)
}

# Difficulty inferred from artifact size + REV iteration count.
def infer_level(content: str, frontmatter: dict) -> int:
    rev_match = re.search(r"REV(\d+)", str(frontmatter.get("re_gate_session_id", "")))
    rev_n = int(rev_match.group(1)) if rev_match else 0
    size = len(content)
    if rev_n >= 5:
        return 4  # multi-rev artifacts are hard targets
    if size > 30000:
        return 4
    if size > 12000:
        return 3
    if size > 4000:
        return 2
    return 1


YAML_FRONTMATTER_RE = re.compile(r"```yaml\s*\n([\s\S]*?)\n```", re.MULTILINE)
# Match "· 041 module-boundary-identification" or just "041 module-boundary-identification"
H1_SKILL_RE = re.compile(r"\b(\d{3})\s+([a-z][a-z0-9-]+)")


def parse_frontmatter(content: str) -> dict | None:
    """Pull the first ```yaml ... ``` block following the H1 title."""
    m = YAML_FRONTMATTER_RE.search(content[:4000])
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None


def extract_skill(content: str, fm: dict, fallback_name: str | None) -> str | None:
    """Try multiple sources for skill name in order of reliability."""
    # 1. YAML frontmatter — most explicit
    skill = (fm or {}).get("producer_skill") or (fm or {}).get("skill_name")
    if skill:
        return skill
    # 2. H1 title pattern "· NNN skill-name"
    h1_match = re.search(r"^#\s+.*$", content, re.MULTILINE)
    if h1_match:
        m = H1_SKILL_RE.search(h1_match.group())
        if m:
            return m.group(2)
    # 3. CSV mapping
    return fallback_name


def build_tasks(artifacts_root: Path) -> list[dict]:
    tasks: list[dict] = []
    seen_skills: dict[str, int] = {}

    for node_dir in sorted(artifacts_root.iterdir()):
        if not node_dir.is_dir():
            continue
        node = node_dir.name
        if node not in NODE_TO_PATH:
            continue
        path_letter = NODE_TO_PATH[node]

        for f in sorted(node_dir.iterdir()):
            if not f.is_file():
                continue
            if f.suffix not in {".md", ".csv", ".sql"}:
                continue

            content = f.read_text(encoding="utf-8", errors="replace")

            # Try YAML frontmatter, then H1 title, then CSV mapping
            fm = parse_frontmatter(content) or {}
            skill = extract_skill(content, fm, CSV_TO_SKILL.get(f.name))
            if not skill:
                # Skip aggregators / quickstart files without a clear skill
                continue

            # Skip .sql companion files (their .md sibling carries the skill)
            if f.suffix == ".sql":
                continue

            # Deduplicate: if a skill emits both .csv and .md, prefer the .md
            # (richer ground truth) and skip the second.
            sid = f"CINEMA-{node}-{skill}"
            if sid in seen_skills:
                # Already have one for this skill; prefer .md over .csv
                prev_idx = seen_skills[sid]
                prev_path = tasks[prev_idx]["expected"]["ground_truth_path"]
                if prev_path.endswith(".md"):
                    continue
                # Replace with this one if richer
                tasks.pop(prev_idx)
                # Reindex
                seen_skills = {s: (i if i < prev_idx else i - 1) for s, i in seen_skills.items() if s != sid}

            level = infer_level(content, fm)
            rev = fm.get("re_gate_session_id", "")
            rev_suffix = f"-{rev}" if rev else ""

            input_text = build_input_description(node, skill, fm, f)

            task = {
                "id": f"CINEMA-{node}-{skill[:24]}{rev_suffix}".replace("_", "-"),
                "path": path_letter,
                "level": level,
                "input": input_text,
                "expected": {
                    "atomic_skill": skill,
                    "ground_truth_path": str(f.resolve()),
                    "ground_truth_schema_version": fm.get("schema_version"),
                    "required_artifacts": [f.name],
                },
                "source_node": node,
                "source_baseline": fm.get("source_baseline") or fm.get("input_baseline"),
                "rev_iteration": rev,
                "known_traps": [
                    "fabricating findings not in PRD",
                    "missing key items the real artifact captured",
                ],
            }
            tasks.append(task)
            seen_skills[sid] = len(tasks) - 1

    return tasks


def build_input_description(node: str, skill: str, fm: dict, path: Path) -> str:
    src = fm.get("source_baseline") or fm.get("input_baseline") or {}
    prd_ver = src.get("prd") if isinstance(src, dict) else None
    parts = [
        f"Given the CinemaAI PRD ({prd_ver or 'v0.3/v0.4'}) describing an AI-driven anime/short-drama production tool",
        "(15 modules, 86+ functions, ~268 PD), and any sibling artifacts already produced upstream,",
        f"produce a {node} {skill} artifact.",
    ]
    if "re_gate_session_id" in fm:
        parts.append(f"This is iteration {fm['re_gate_session_id']} — incorporate prior session findings.")
    parts.append(
        f"The ground truth is at: {path.name} (full path embedded in expected.ground_truth_path)."
    )
    return " ".join(parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default=r"D:/projects/python/ai_work/video/cinemaai/CinemaAI-PRD",
        help="Path to the CinemaAI-PRD directory",
    )
    parser.add_argument("--out", default="tasks_cinemaai.yaml")
    args = parser.parse_args()

    artifacts_root = Path(args.root) / "工作产物"
    if not artifacts_root.exists():
        raise SystemExit(f"工作产物 not found at: {artifacts_root}")

    tasks = build_tasks(artifacts_root)

    # Sort: by node, then by skill
    tasks.sort(key=lambda t: (t["source_node"], t["id"]))

    # Write
    out_path = Path(args.out)
    out_path.write_text(
        yaml.dump(tasks, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )

    # Summary
    print(f"Built {len(tasks)} ground-truth tasks → {out_path.resolve()}")
    by_node: dict[str, int] = {}
    by_path: dict[str, int] = {}
    by_level: dict[int, int] = {}
    for t in tasks:
        by_node[t["source_node"]] = by_node.get(t["source_node"], 0) + 1
        by_path[t["path"]] = by_path.get(t["path"], 0) + 1
        by_level[t["level"]] = by_level.get(t["level"], 0) + 1
    print("By node:  ", dict(sorted(by_node.items())))
    print("By path:  ", dict(sorted(by_path.items())))
    print("By level: ", dict(sorted(by_level.items())))


if __name__ == "__main__":
    main()
