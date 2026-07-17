"""LLM-as-judge: scores model responses on each dimension.

Judges are regular providers — Gemini Flash / Groq Llama keep scoring free.
Pass multiple judges to average scores and reduce single-model bias.
"""

from __future__ import annotations

import json
import re
import statistics
from typing import Iterable

from challenges import Challenge
from providers import get_provider, pick_default_judge, display_name

DEFAULT_JUDGE_MODEL = "gemini-2.0-flash"  # free by default; overridden if unconfigured

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

Respond ONLY with valid JSON in this exact shape (no markdown fences, no commentary):
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


def _strip_fences(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        if len(parts) >= 2:
            raw = parts[1]
            if raw.startswith("json"):
                raw = raw[4:]
    return raw.strip()


def _extract_json(raw: str) -> dict:
    """Parse judge JSON, with a brace-slice fallback for chatty models."""
    cleaned = _strip_fences(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if not match:
            raise
        return json.loads(match.group(0))


def _normalize(scores: dict) -> dict:
    return {
        "correctness": _clamp(scores.get("correctness")),
        "quality": _clamp(scores.get("quality")),
        "documentation": _clamp(scores.get("documentation")),
        "notes": str(scores.get("notes", "")),
    }


def score_response(
    challenge: Challenge,
    response: str,
    model_id: str,
    judge_model: str | None = None,
) -> dict:
    """Ask one judge model to score a response."""
    judge_model = judge_model or pick_default_judge()
    prompt = JUDGE_PROMPT.format(
        challenge_name=challenge.name,
        prompt=challenge.prompt,
        rubric_correctness=challenge.rubric["correctness"],
        rubric_quality=challenge.rubric["quality"],
        rubric_documentation=challenge.rubric["documentation"],
        response=response[:6000],
    )

    provider = get_provider(judge_model)
    if not provider:
        msg = f"judge {judge_model} not configured"
        print(f"\n  [judge error for {model_id}]: {msg}")
        return {
            "correctness": 0,
            "quality": 0,
            "documentation": 0,
            "notes": f"judge error: {msg}",
            "judge": judge_model,
        }

    try:
        raw = provider.complete(prompt, max_tokens=1024)
        scores = _normalize(_extract_json(raw))
        scores["judge"] = judge_model
        return scores
    except Exception as e:
        print(f"\n  [judge error for {model_id} via {judge_model}]: {e}")
        return {
            "correctness": 0,
            "quality": 0,
            "documentation": 0,
            "notes": f"judge error: {e}",
            "judge": judge_model,
        }


def score_response_multi(
    challenge: Challenge,
    response: str,
    model_id: str,
    judges: Iterable[str],
) -> dict:
    """Score with multiple judges and average the numeric dimensions.

    Notes become a short panel: `judge: note; judge2: note2`.
    """
    judge_list = [j.strip() for j in judges if j and j.strip()]
    if not judge_list:
        judge_list = [pick_default_judge()]

    if len(judge_list) == 1:
        return score_response(challenge, response, model_id, judge_list[0])

    panels: list[dict] = []
    for j in judge_list:
        panels.append(score_response(challenge, response, model_id, j))

    correctness = statistics.fmean(p["correctness"] for p in panels)
    quality = statistics.fmean(p["quality"] for p in panels)
    documentation = statistics.fmean(p["documentation"] for p in panels)
    notes_parts = []
    for p in panels:
        j = p.get("judge", "?")
        n = (p.get("notes") or "").strip()
        if n:
            notes_parts.append(f"{display_name(j)}: {n}")

    return {
        "correctness": round(correctness, 2),
        "quality": round(quality, 2),
        "documentation": round(documentation, 2),
        "notes": " | ".join(notes_parts)[:800],
        "judge": "+".join(judge_list),
        "judge_panel": panels,
    }
