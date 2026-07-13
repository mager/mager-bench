"""
mager-bench — rates coding models on correctness, code quality, docs, and speed.

Usage:
    python bench.py                            # run all challenges, all models
    python bench.py --models claude-sonnet-5,gpt-4o
    python bench.py --challenge fizzbuzz       # one challenge
    python bench.py --judge claude-opus-4-8    # score with a different judge
    python bench.py --serial                   # one model at a time (cleaner latency numbers)
    python bench.py --output results.json      # save results
"""

from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from providers import get_provider, AVAILABLE_MODELS
from judge import score_response, DEFAULT_JUDGE_MODEL
from challenges import load_challenges


@dataclass
class Result:
    model: str
    challenge: str
    response: str
    correctness: float   # 0–10
    quality: float       # 0–10
    documentation: float # 0–10
    speed_ms: int
    total_score: float
    notes: str


def run_model_on_challenge(challenge, model_id: str, judge_model: str) -> tuple[Result | None, str]:
    """Run one model against one challenge and judge the result.

    Returns (result, status_line); result is None when the model was skipped or errored.
    """
    provider = get_provider(model_id)
    if not provider:
        return None, f"{model_id}: no API key configured, skipping"

    t0 = time.perf_counter()
    try:
        response = provider.complete(challenge.prompt)
    except Exception as e:
        return None, f"{model_id}: ERROR: {e}"
    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    scores = score_response(challenge, response, model_id, judge_model=judge_model)
    total = round((scores["correctness"] + scores["quality"] + scores["documentation"]) / 3, 1)

    result = Result(
        model=model_id,
        challenge=challenge.name,
        response=response,
        correctness=scores["correctness"],
        quality=scores["quality"],
        documentation=scores["documentation"],
        speed_ms=elapsed_ms,
        total_score=total,
        notes=scores.get("notes", ""),
    )
    return result, f"{model_id}: total={total:.1f}  ({elapsed_ms}ms)"


def run_benchmark(
    models: list[str],
    challenge_names: list[str] | None,
    judge_model: str,
    serial: bool = False,
) -> list[Result]:
    challenges = load_challenges(challenge_names)
    results: list[Result] = []

    for challenge in challenges:
        print(f"\n── {challenge.name} ──────────────────────────────────")
        if serial:
            for model_id in models:
                result, line = run_model_on_challenge(challenge, model_id, judge_model)
                print(f"  {line}")
                if result:
                    results.append(result)
        else:
            with ThreadPoolExecutor(max_workers=len(models)) as pool:
                futures = {
                    pool.submit(run_model_on_challenge, challenge, m, judge_model): m
                    for m in models
                }
                for future in as_completed(futures):
                    result, line = future.result()
                    print(f"  {line}")
                    if result:
                        results.append(result)

    return results


def print_table(results: list[Result], judge_model: str) -> None:
    if not results:
        return
    print("\n\n═══ RESULTS ═══════════════════════════════════════════════════")
    print(f"Judge: {judge_model}")
    print(f"{'Model':<30} {'Challenge':<20} {'Correct':>7} {'Quality':>7} {'Docs':>7} {'Speed':>8} {'Total':>7}")
    print("─" * 90)

    sorted_results = sorted(results, key=lambda r: -r.total_score)
    for r in sorted_results:
        speed = f"{r.speed_ms}ms"
        print(f"{r.model:<30} {r.challenge:<20} {r.correctness:>7.1f} {r.quality:>7.1f} {r.documentation:>7.1f} {speed:>8} {r.total_score:>7.1f}")

    # per-model averages
    by_model: dict[str, list[Result]] = {}
    for r in results:
        by_model.setdefault(r.model, []).append(r)

    print("\n── Averages ─────────────────────────────────────────────────")
    ranked = sorted(by_model.items(), key=lambda kv: -sum(r.total_score for r in kv[1]) / len(kv[1]))
    for model, rs in ranked:
        avg_total = sum(r.total_score for r in rs) / len(rs)
        avg_speed = sum(r.speed_ms for r in rs) // len(rs)
        print(f"  {model:<30} avg={avg_total:.1f}  avg_speed={avg_speed}ms")


def main() -> None:
    parser = argparse.ArgumentParser(description="mager-bench: coding model benchmark")
    parser.add_argument("--models", default=",".join(AVAILABLE_MODELS), help="comma-separated model IDs")
    parser.add_argument("--challenge", default=None, help="run a single challenge by name")
    parser.add_argument("--judge", default=DEFAULT_JUDGE_MODEL, help="Anthropic model ID used to score responses")
    parser.add_argument("--serial", action="store_true", help="run models one at a time instead of in parallel")
    parser.add_argument("--output", default=None, help="save results to JSON file")
    parser.add_argument("--list-models", action="store_true", help="list configured models and exit")
    parser.add_argument("--list-challenges", action="store_true", help="list challenges and exit")
    args = parser.parse_args()

    if args.list_models:
        print("Available models:", ", ".join(AVAILABLE_MODELS))
        return

    if args.list_challenges:
        for c in load_challenges(None):
            print(f"  {c.name}: {c.description}")
        return

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    challenge_names = [args.challenge] if args.challenge else None

    results = run_benchmark(models, challenge_names, args.judge, serial=args.serial)
    print_table(results, args.judge)

    if args.output:
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "judge": args.judge,
            "results": [asdict(r) for r in results],
        }
        Path(args.output).write_text(json.dumps(payload, indent=2))
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
