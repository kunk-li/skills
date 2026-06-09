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
    if name in ("openai", "qwen", "openai-compat", "deepseek"):
        return OpenAICompatibleAdapter()
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
        candidate = m.group(0) if m else text

        def _repair(s):
            # Best-effort: close an unterminated string + balance open braces/
            # brackets so a TRUNCATED response (model hit max_tokens mid-string)
            # still yields its partial artifacts instead of zeroing every
            # dimension. Returns None when there is nothing to fix.
            if not s:
                return None
            out, in_str, esc, stack = [], False, False, []
            for ch in s:
                out.append(ch)
                if esc:
                    esc = False
                elif ch == "\\" and in_str:
                    esc = True
                elif ch == '"':
                    in_str = not in_str
                elif not in_str and ch in "{[":
                    stack.append(ch)
                elif not in_str and ch in "}]" and stack:
                    stack.pop()
            if in_str:
                out.append('"')
            out.extend("}" if c == "{" else "]" for c in reversed(stack))
            repaired = "".join(out)
            return repaired if repaired != s else None

        # strict=False tolerates literal control chars inside string values; the
        # repair pass rescues truncated JSON. Try as-is, then repaired.
        for attempt in (candidate, _repair(candidate)):
            if not attempt:
                continue
            try:
                data = json.loads(attempt, strict=False)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                data.setdefault("selected_skills", [])
                data.setdefault("artifacts", {})
                return data
        return {"selected_skills": [], "artifacts": {}, "raw": text,
                "parse_error": "unparseable"}


class OpenAICompatibleAdapter:
    """Calls any OpenAI-compatible chat API (DashScope/Qwen, DeepSeek, GLM...).

    D-012: use a free/owned model, not a paid Anthropic key. Reads
    SS_LLM_API_KEY / SS_LLM_BASE_URL / SS_LLM_MODEL from env (falls back
    to OPENAI_* and DashScope qwen-plus). Judge defaults to a cheaper/
    faster model (qwen-turbo) overridable via SS_LLM_JUDGE_MODEL.
    Same contract as ClaudeAdapter.
    """

    def __init__(self, model=None, judge_model=None, skills_index_path=None):
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError("openai SDK not installed. Run: pip install openai") from e
        api_key = os.environ.get("SS_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("SS_LLM_API_KEY / OPENAI_API_KEY env var not set")
        base_url = os.environ.get("SS_LLM_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model or os.environ.get("SS_LLM_MODEL") or "qwen-plus"
        self.judge_model = judge_model or os.environ.get("SS_LLM_JUDGE_MODEL") or "qwen-turbo"
        self.skills_index = ClaudeAdapter._load_skills_index(self, skills_index_path)
        # SS_EVAL_INJECT_SKILL=1 (default): inject the expected skill's SKILL.md so the
        # eval measures the SKILL's guidance quality, not the model's raw free-forming.
        self.inject_skill = os.environ.get("SS_EVAL_INJECT_SKILL", "1") != "0"
        self._skill_cache = {}

    def _chat(self, messages, model, max_tokens):
        resp = self.client.chat.completions.create(
            model=model, messages=messages, max_tokens=max_tokens, temperature=0.3,
        )
        return resp.choices[0].message.content or ""

    def _load_skill_md(self, skill_name):
        """Find <skill_name>'s zip in the library and return its SKILL.md text."""
        if not skill_name:
            return None
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]
        import glob as _glob
        import zipfile as _zip
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        hits = _glob.glob(os.path.join(root, "完稿", "**", f"*{skill_name}*.zip"), recursive=True)
        md = None
        if hits:
            zf = _zip.ZipFile(hits[0])
            sk = [n for n in zf.namelist() if n.endswith("SKILL.md")]
            if sk:
                md = zf.read(sk[0]).decode("utf-8", "replace")
        self._skill_cache[skill_name] = md
        return md

    def run(self, input_text, task=None):
        exp = (task or {}).get("expected", {})
        skill_name = exp.get("atomic_skill") or exp.get("macro_skill")
        required = exp.get("required_artifacts") or []
        fname = required[0] if required else "output.md"
        skill_md = self._load_skill_md(skill_name) if self.inject_skill else None

        if skill_md:
            # Skill-injected mode: measure the SKILL's instructions, not raw model ability.
            system = (
                f"You are applying the skill `{skill_name}`. Follow its instructions exactly "
                "to produce the required artifact for the user's input.\n\n"
                f"=== SKILL.md ({skill_name}) ===\n{skill_md}\n=== END SKILL.md ===\n\n"
                "Output a single valid JSON object — no prose before or after:\n"
                f'{{"selected_skills": ["{skill_name}"], '
                f'"artifacts": {{"{fname}": "...full artifact content per the skill..."}}}}\n'
                "The artifact value must be the full content the skill prescribes."
            )
        else:
            system = (
                "You are an agent with access to a library of macro and atomic skills.\n\n"
                f"{self.skills_index}\n\n"
                "Decide which skill(s) to invoke and produce the artifacts they require.\n"
                "Output a single valid JSON object — no prose:\n"
                '{"selected_skills": ["skill-name"], "artifacts": {"filename.md": "...content..."}}'
            )
        text = self._chat(
            [{"role": "system", "content": system}, {"role": "user", "content": input_text}],
            self.model, int(os.environ.get("SS_EVAL_MAX_TOKENS") or 8192),
        )
        return ClaudeAdapter._parse(self, text)

    def judge(self, prompt):
        text = self._chat(
            [{"role": "user", "content": prompt + "\n\nReturn ONLY a decimal number between 0.0 and 1.0."}],
            self.judge_model, 20,
        )
        m = re.search(r"(\d+(?:\.\d+)?)", text.strip())
        if not m:
            return 0.5
        try:
            return max(0.0, min(1.0, float(m.group(1))))
        except ValueError:
            return 0.5
