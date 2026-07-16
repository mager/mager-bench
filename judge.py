"""LLM-as-judge: uses Claude to score model responses on each dimension."""

from __future__ import annotations

import os
import json
import anthropic
from challenges import Challenge

DEFAULT_JUDGE_MODEL = "claude-sonnet-5"

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


# Structured-output schema — the API guarantees the judge's reply parses as
# exactly this shape. Numeric ranges can't be expressed in the schema subset,
# so scores are clamped to 0-10 after parsing.
JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "correctness": {"type": "number", "description": "Score from 0 to 10"},
        "quality": {"type": "number", "description": "Score from 0 to 10"},
        "documentation": {"type": "number", "description": "Score from 0 to 10"},
        "notes": {
            "type": "string",
            "description": "One sentence summary of key strengths or weaknesses",
        },
    },
    "required": ["correctness", "quality", "documentation", "notes"],
    "additionalProperties": False,
}

JUDGE_PROMPT = """You are an expert code reviewer judging a model's response to a coding challenge.

Challenge: {challenge_name}
Task given to the model:
{prompt}

Rubric:
- Correctness: {rubric_correctness}
- Code Quality: {rubric_quality}
- Documentation: {rubric_documentation}

Model's response:
<response>
{response}
</response>

Score each dimension from 0 to 10. Be critical and precise — reserve 9-10 for genuinely excellent work.

Respond ONLY with valid JSON in this exact shape:
{{
  "correctness": <number 0-10>,
  "quality": <number 0-10>,
  "documentation": <number 0-10>,
  "notes": "<one sentence summary of key strengths or weaknesses>"
}}"""


def _clamp(value) -> float:
    try:
        return max(0.0, min(10.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def _extract_text(msg) -> str:
    # skip thinking blocks (extended thinking models emit these before text)
    for block in msg.content:
        if block.type == "text":
            return block.text.strip()
    raise ValueError(f"no text block in judge response (stop_reason={msg.stop_reason}, blocks={[b.type for b in msg.content]})")


def _strip_fences(raw: str) -> str:
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


def score_response(
    challenge: Challenge,
    response: str,
    model_id: str,
    judge_model: str = DEFAULT_JUDGE_MODEL,
) -> dict:
    """Ask the judge model to score a response. Returns dict with correctness/quality/documentation/notes."""
    prompt = JUDGE_PROMPT.format(
        challenge_name=challenge.name,
        prompt=challenge.prompt,
        rubric_correctness=challenge.rubric["correctness"],
        rubric_quality=challenge.rubric["quality"],
        rubric_documentation=challenge.rubric["documentation"],
        response=response[:6000],  # trim very long responses
    )

    try:
        client = _get_client()
        msg = client.messages.create(
            model=judge_model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = _strip_fences(_extract_text(msg))

        scores = json.loads(raw)
        return {
            "correctness": _clamp(scores.get("correctness")),
            "quality": _clamp(scores.get("quality")),
            "documentation": _clamp(scores.get("documentation")),
            "notes": str(scores.get("notes", "")),
        }
    except Exception as e:
        print(f"\n  [judge error for {model_id}]: {e}")
        return {"correctness": 0, "quality": 0, "documentation": 0, "notes": f"judge error: {e}"}
