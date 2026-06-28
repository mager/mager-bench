"""LLM-as-judge: uses Claude to score model responses on each dimension."""

import os
import json
import anthropic
from challenges import Challenge

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


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


def score_response(challenge: Challenge, response: str, model_id: str) -> dict:
    """Ask Claude to score a model response. Returns dict with correctness/quality/documentation/notes."""
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
            model="claude-sonnet-4-6",  # use Sonnet for judging — fast and cheap
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        # strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        print(f"\n  [judge error for {model_id}]: {e}")
        return {"correctness": 0, "quality": 0, "documentation": 0, "notes": f"judge error: {e}"}
