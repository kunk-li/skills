"""Agent adapters.

MockAdapter   — offline, scripted responses; for testing the framework itself.
ClaudeAdapter — Anthropic SDK; production eval against Claude. Requires
                ANTHROPIC_API_KEY env var.

The adapter contract:
    run(input_text, task) -> response dict with shape:
        {
            "selected_skills": [str],     # which skill(s) the agent chose
            "artifacts": {filename: text} # produced artifacts (md / yaml / json)
            "trace": [{step, skill, ...}] # optional internal steps
        }
    judge(prompt_text) -> float in [0, 1]
"""

import hashlib
import json
import os
import re


def get_adapter(name: str):
    if name == "mock":
        return MockAdapter()
    if name == "claude":
        return ClaudeAdapter()
    raise ValueError(f"Unknown adapter: {name}")


class MockAdapter:
    """Returns deterministic scripted responses.

    Default behaviour: returns a plausible-looking response so the eval
    framework itself can be tested end-to-end. For each task you can put
    a fixture file under fixtures/<task_id>.json which will be loaded
    verbatim.
    """

    def __init__(self, fixtures_dir="fixtures"):
        self.fixtures_dir = fixtures_dir

    def run(self, input_text, task=None):
        # Try a fixture first
        if task:
            fx = os.path.join(self.fixtures_dir, f"{task['id']}.json")
            if os.path.exists(fx):
                with open(fx, encoding="utf-8") as f:
                    return json.load(f)

        # Default scripted response — guesses the macro skill from the task
        expected = (task or {}).get("expected", {})
        macro = expected.get("macro_skill", "requirement-to-prd")
        required = expected.get("required_artifacts", ["output.md"])
        return {
            "selected_skills": [macro],
            "artifacts": {
                f: f"# Mock {f}\n\n(scripted mock output for {task['id'] if task else 'unknown'})\n"
                for f in required
            },
            "trace": [{"step": 1, "skill": macro, "duration_ms": 100}],
        }

    def judge(self, prompt):
        # Stable pseudo-random based on prompt hash for reproducibility
        h = int(hashlib.md5(prompt.encode("utf-8")).hexdigest(), 16)
        return 0.5 + (h % 50) / 100.0  # 0.5 - 0.99


class ClaudeAdapter:
    """Calls Anthropic API. Requires ANTHROPIC_API_KEY."""

    DEFAULT_MODEL = "claude-opus-4-7"
    DEFAULT_JUDGE_MODEL = "claude-haiku-4-5-20251001"

    def __init__(self, model=None, judge_model=None, skills_index_path=None):
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise RuntimeError(
                "anthropic SDK not installed. Run: pip install anthropic"
            ) from e
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY env var not set")
        self.client = Anthropic(api_key=api_key)
        self.model = model or self.DEFAULT_MODEL
        self.judge_model = judge_model or self.DEFAULT_JUDGE_MODEL
        self.skills_index = self._load_skills_index(skills_index_path)

    def _load_skills_index(self, path):
        """Load the skills catalog (name + description) for the agent to
        pick from. If not provided, uses a minimal fallback list of macro
        skills.
        """
        if path and os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return f.read()
        # Minimal fallback: just list macros
        return """Available macro skills:
- requirement-to-prd: vague need → review-ready PRD
- prd-to-tech-solution: PRD → tech solution + API + schema
- solution-to-dev-tasks: solution → sprint-ready task list
- diff-to-pr-ready: git diff → risk report + PR description + commit message
- incident-to-postmortem: production symptom → root cause + containment + prevention

(155 atomic skills available; prefer macros unless the task is narrow.)
"""

    def run(self, input_text, task=None):
        system = f"""You are an agent with access to a library of macro skills and atomic skills.

{self.skills_index}

Given the user's input, decide which skill(s) to invoke and produce the artifacts they require.

Output a single valid JSON object with this shape — no prose before or after:
{{
  "selected_skills": ["skill-name", ...],
  "artifacts": {{
    "filename.md": "...full content...",
    "another.yaml": "...full content..."
  }},
  "trace": [{{"step": 1, "skill": "name", "note": "what happened"}}]
}}

Rules:
- Pick the most specific skill. Prefer macro skills for multi-step tasks.
- If the request is too narrow for a macro, use an atomic skill instead.
- If the request is ambiguous, you may emit selected_skills=[] and ask in artifacts.
- artifacts values must be strings.
"""
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=system,
            messages=[{"role": "user", "content": input_text}],
        )
        text = resp.content[0].text
        return self._parse(text)

    def judge(self, prompt):
        resp = self.client.messages.create(
            model=self.judge_model,
            max_tokens=20,
            messages=[
                {
                    "role": "user",
                    "content": prompt + "\n\nReturn ONLY a decimal number between 0.0 and 1.0.",
                }
            ],
        )
        text = resp.content[0].text.strip()
        m = re.search(r"(\d+(?:\.\d+)?)", text)
        if not m:
            return 0.5
        try:
            v = float(m.group(1))
            return max(0.0, min(1.0, v))
        except ValueError:
            return 0.5

    def _parse(self, text):
        # Extract first JSON object (greedy on outermost braces)
        m = re.search(r"\{[\s\S]*\}", text)
        if not m:
            return {"selected_skills": [], "artifacts": {}, "raw": text, "parse_error": "no_json"}
        try:
            data = json.loads(m.group(0))
            data.setdefault("selected_skills", [])
            data.setdefault("artifacts", {})
            return data
        except json.JSONDecodeError as e:
            return {"selected_skills": [], "artifacts": {}, "raw": text, "parse_error": str(e)}
