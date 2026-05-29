"""Skills eval runner.

Usage:
    python eval.py --adapter mock                       # smoke test, no API cost
    python eval.py --adapter claude --only A1 D2        # specific tasks
    python eval.py --adapter claude                     # full 25-task run
    python eval.py --adapter claude --paths A B         # only path A and B
    python eval.py --adapter claude --levels 1 2        # only L1-L2

Outputs:
    reports/<timestamp>/results.json    machine-readable
    reports/<timestamp>/summary.md      human-readable rollup
    reports/<timestamp>/raw/<id>.json   per-task raw response

Setup:
    pip install anthropic pyyaml
    export ANTHROPIC_API_KEY=sk-ant-...      # for --adapter claude
"""

import argparse
import datetime
import json
import sys
import time
from pathlib import Path

import yaml

from adapters import get_adapter
from scorers import score_response, DIMENSIONS, GROUND_TRUTH_DIMENSIONS


def run_eval(
    tasks_file: str,
    adapter_name: str,
    out_dir: str,
    only_tasks=None,
    only_paths=None,
    only_levels=None,
):
    tasks = yaml.safe_load(Path(tasks_file).read_text(encoding="utf-8"))
    adapter = get_adapter(adapter_name)

    # Filtering
    filtered = []
    for t in tasks:
        if only_tasks and t["id"] not in only_tasks:
            continue
        if only_paths and t["path"] not in only_paths:
            continue
        if only_levels and t["level"] not in only_levels:
            continue
        filtered.append(t)
    if not filtered:
        print("No tasks matched filters.", file=sys.stderr)
        return 1

    # Output dir
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_root = Path(out_dir) / stamp
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "raw").mkdir(exist_ok=True)

    results = []
    for i, task in enumerate(filtered, 1):
        print(f"[{i}/{len(filtered)}] {task['id']} (L{task['level']} {task['path']})...", flush=True)
        start = time.time()
        try:
            response = adapter.run(task["input"], task=task)
        except Exception as e:
            response = {"error": str(e), "selected_skills": [], "artifacts": {}}
        duration_ms = int((time.time() - start) * 1000)

        scores = score_response(task, response, adapter)
        total = sum(scores.values())
        verdict = "PASS" if total >= 4 else ("WEAK" if total >= 3 else "FAIL")

        result = {
            "task_id": task["id"],
            "path": task["path"],
            "level": task["level"],
            "duration_ms": duration_ms,
            "scores": scores,
            "total": total,
            "verdict": verdict,
        }
        results.append(result)

        # Save raw per-task
        (out_root / "raw" / f"{task['id']}.json").write_text(
            json.dumps({"task": task, "response": response, "result": result}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        print(f"    {verdict}  scores={scores}  total={total:.1f}/5")

    # Aggregate
    (out_root / "results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    summary = build_summary(results, adapter_name)
    (out_root / "summary.md").write_text(summary, encoding="utf-8")

    print(f"\nDone. Reports written to: {out_root}")
    print("---")
    print(summary[:2000])
    return 0


def build_summary(results, adapter_name):
    total_runs = len(results)
    pass_count = sum(1 for r in results if r["verdict"] == "PASS")
    weak_count = sum(1 for r in results if r["verdict"] == "WEAK")
    fail_count = sum(1 for r in results if r["verdict"] == "FAIL")
    avg_total = sum(r["total"] for r in results) / total_runs if total_runs else 0

    # By path
    by_path = {}
    for r in results:
        by_path.setdefault(r["path"], []).append(r)

    # By level
    by_level = {}
    for r in results:
        by_level.setdefault(r["level"], []).append(r)

    # By dimension — dynamic, since GT tasks have gt_similarity instead of utility
    all_dims = set(DIMENSIONS) | set(GROUND_TRUTH_DIMENSIONS)
    by_dim = {d: [] for d in all_dims}
    for r in results:
        for d, v in r["scores"].items():
            by_dim[d].append(v)
    # Keep stable display order
    by_dim_ordered = [d for d in (list(DIMENSIONS) + ["gt_similarity"]) if by_dim[d]]

    lines = []
    lines.append(f"# Eval Summary · {adapter_name}\n")
    lines.append(f"- Total tasks: {total_runs}")
    lines.append(f"- PASS / WEAK / FAIL:  {pass_count} / {weak_count} / {fail_count}")
    lines.append(f"- Avg total score: {avg_total:.2f} / 5.0\n")

    lines.append("## By path\n")
    lines.append("| path | runs | pass | avg |")
    lines.append("|---|---|---|---|")
    for path in sorted(by_path):
        rs = by_path[path]
        p = sum(1 for r in rs if r["verdict"] == "PASS")
        avg = sum(r["total"] for r in rs) / len(rs)
        lines.append(f"| {path} | {len(rs)} | {p}/{len(rs)} | {avg:.2f} |")
    lines.append("")

    lines.append("## By level\n")
    lines.append("| level | runs | pass | avg |")
    lines.append("|---|---|---|---|")
    for lvl in sorted(by_level):
        rs = by_level[lvl]
        p = sum(1 for r in rs if r["verdict"] == "PASS")
        avg = sum(r["total"] for r in rs) / len(rs)
        lines.append(f"| L{lvl} | {len(rs)} | {p}/{len(rs)} | {avg:.2f} |")
    lines.append("")

    lines.append("## By dimension (avg)\n")
    lines.append("| dimension | runs | avg | min | runs<0.5 |")
    lines.append("|---|---|---|---|---|")
    for d in by_dim_ordered:
        scores = by_dim[d]
        avg = sum(scores) / len(scores)
        mn = min(scores)
        weak = sum(1 for s in scores if s < 0.5)
        lines.append(f"| {d} | {len(scores)} | {avg:.2f} | {mn:.2f} | {weak} |")
    lines.append("")

    lines.append("## Per-task results\n")
    lines.append("| id | path | L | verdict | sel | comp | gnd | fmt | util/gt | total |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in results:
        s = r["scores"]
        last = s.get("utility", s.get("gt_similarity", 0.0))
        lines.append(
            f"| {r['task_id']} | {r['path']} | {r['level']} | {r['verdict']} | "
            f"{s['selection']:.1f} | {s['completeness']:.1f} | {s['groundedness']:.1f} | "
            f"{s['format']:.1f} | {last:.1f} | **{r['total']:.1f}** |"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", default="tasks.yaml")
    parser.add_argument("--adapter", default="mock", choices=["mock", "claude"])
    parser.add_argument("--only", nargs="+", help="Specific task IDs (e.g. A1 D2)")
    parser.add_argument("--paths", nargs="+", help="Filter by path (A B C D E)")
    parser.add_argument("--levels", nargs="+", type=int, help="Filter by level (1-5)")
    parser.add_argument("--out", default="reports")
    args = parser.parse_args()

    sys.exit(
        run_eval(
            args.tasks, args.adapter, args.out, args.only, args.paths, args.levels
        )
    )
