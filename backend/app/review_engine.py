import json, re
from .llm_client import OllamaClient

PROMPT_TEMPLATE = """
You are a structured code-review assistant. Produce ONLY a valid JSON array of objects.
Each object MUST have these keys:
- file_path
- line_start
- line_end
- category (readability|performance|security|style)
- severity (low|medium|high)
- message
- suggestion

Persona: {persona}

Diff:
{diff}

Produce ONLY the JSON array and nothing else.
"""

def build_prompt(diff_text: str, persona: str = "mentor") -> str:
    return PROMPT_TEMPLATE.format(persona=persona, diff=diff_text)

def sanitize_model_output(raw: str) -> str:
    """
    Extract first JSON array from model output defensively.
    """
    start = raw.find('[')
    end = raw.rfind(']') + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON array found in model output")
    return raw[start:end]

def run_review(diff_text: str, persona: str, client: OllamaClient):
    prompt = build_prompt(diff_text, persona)
    raw = client.run_prompt(prompt)
    try:
        j = json.loads(sanitize_model_output(raw))
    except Exception as e:
        raise RuntimeError("Failed to parse LLM output as JSON array") from e

    # minimal validation
    if not isinstance(j, list):
        raise RuntimeError("LLM output JSON is not a list")
    for item in j:
        if not isinstance(item, dict) or "file_path" not in item:
            raise RuntimeError("Malformed item in LLM output")
    return j
