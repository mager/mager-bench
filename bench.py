"""
mager-bench — rates coding models on correctness, code quality, docs, and speed.

Usage:
    python bench.py                            # free/cheap models, free judge
    python bench.py --tier free                # wallet-safe only
    python bench.py --models llama-3.3-70b,gemini-2.0-flash
    python bench.py --challenge fizzbuzz
    python bench.py --judge gemini-2.0-flash   # free judge
    python bench.py --judges gemini-2.0-flash,llama-3.3-70b
    python bench.py --runs 3                   # mean ± stddev across runs
    python bench.py --serial
    python bench.py --output results.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # optional — keys may already be in the environment

from providers import (
    AVAILABLE_MODELS,
    CHEAP_MODELS,
    FREE_MODELS,
    PAID_MODELS,
    configured_models,
    display_name,
    get_provider,
    list_models_report,
    model_info,
    pick_default_judge,
)
from judge import score_response_multi, DEFAULT_JUDGE_MODEL
from challenges import load_challenges


@dataclass
class Result:
    model: str
    challenge: str
    response: str
    correctness: float
    quality: float
    documentation: float
    speed_ms: int
    total_score: float
    notes: str
    judge: str = ""
    run: int = 1
    # populated when --runs > 1 after aggregation
    runs: int = 1
    stddev: float | None = None
    scores_per_run: list[float] = field(default_factory=list)


def run_model_on_challenge(
    challenge,
    model_id: str,
    judges: list[str],
    run: int = 1,
) -> tuple[Result | None, str]:
    provider = get_provider(model_id)
    if not provider:
        return None, f"{model_id}: no API key configured, skipping"

    t0 = time.perf_counter()
    try:
        response = provider.complete(challenge.prompt)
    except Exception as e:
        return None, f"{model_id}: ERROR: {e}"
    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    scores = score_response_multi(challenge, response, model_id, judges)
    total = round(
        (scores["correctness"] + scores["quality"] + scores["documentation"]) / 3, 1
    )
    judge_label = scores.get("judge") or "+".join(judges)

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
        judge=judge_label,
        run=run,
        runs=1,
        scores_per_run=[total],
    )
    run_tag = f" r{run}" if run > 1 else ""
    return result, f"{model_id}{run_tag}: total={total:.1f}  ({elapsed_ms}ms)"


def aggregate_runs(results: list[Result]) -> list[Result]:
    """Collapse (model, challenge) multi-run results into mean ± stddev rows."""
    buckets: dict[tuple[str, str], list[Result]] = {}
    for r in results:
        buckets.setdefault((r.model, r.challenge), []).append(r)

    out: list[Result] = []
    for (model, challenge), group in buckets.items():
        if len(group) == 1:
            out.append(group[0])
            continue
        # keep the longest response (usually last) for paper-trail
        best = max(group, key=lambda x: len(x.response))
        totals = [g.total_score for g in group]
        mean_total = round(statistics.fmean(totals), 1)
        std = round(statistics.pstdev(totals), 2) if len(totals) > 1 else 0.0
        out.append(
            Result(
                model=model,
                challenge=challenge,
                response=best.response,
                correctness=round(statistics.fmean(g.correctness for g in group), 2),
                quality=round(statistics.fmean(g.quality for g in group), 2),
                documentation=round(statistics.fmean(g.documentation for g in group), 2),
                speed_ms=int(statistics.fmean(g.speed_ms for g in group)),
                total_score=mean_total,
                notes=best.notes,
                judge=best.judge,
                run=1,
                runs=len(group),
                stddev=std,
                scores_per_run=totals,
            )
        )
    return out


def run_benchmark(
    models: list[str],
    challenge_names: list[str] | None,
    judges: list[str],
    serial: bool = False,
    runs: int = 1,
) -> list[Result]:
    challenges = load_challenges(challenge_names)
    results: list[Result] = []

    for challenge in challenges:
        print(f"\n── {challenge.name} ──────────────────────────────────")
        jobs: list[tuple[str, int]] = [
            (m, run) for run in range(1, runs + 1) for m in models
        ]

        if serial:
            for model_id, run in jobs:
                result, line = run_model_on_challenge(challenge, model_id, judges, run)
                print(f"  {line}")
                if result:
                    results.append(result)
        else:
            workers = min(8, max(1, len(jobs)))
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {
                    pool.submit(run_model_on_challenge, challenge, m, judges, run): (m, run)
                    for m, run in jobs
                }
                for future in as_completed(futures):
                    result, line = future.result()
                    print(f"  {line}")
                    if result:
                        results.append(result)

    if runs > 1:
        results = aggregate_runs(results)
    return results


def print_table(results: list[Result], judges: list[str], runs: int) -> None:
    if not results:
        return
    print("\n\n═══ RESULTS ═══════════════════════════════════════════════════")
    print(f"Judge(s): {' + '.join(judges)}   runs={runs}")
    header = f"{'Model':<28} {'Challenge':<16} {'Correct':>7} {'Quality':>7} {'Docs':>7} {'Speed':>8} {'Total':>7}"
    if runs > 1:
        header += f" {'±σ':>6}"
    print(header)
    print("─" * (len(header) + 2))

    sorted_results = sorted(results, key=lambda r: -r.total_score)
    for r in sorted_results:
        speed = f"{r.speed_ms}ms"
        line = (
            f"{r.model:<28} {r.challenge:<16} {r.correctness:>7.1f} "
            f"{r.quality:>7.1f} {r.documentation:>7.1f} {speed:>8} {r.total_score:>7.1f}"
        )
        if runs > 1 and r.stddev is not None:
            line += f" {r.stddev:>6.2f}"
        print(line)

    by_model: dict[str, list[Result]] = {}
    for r in results:
        by_model.setdefault(r.model, []).append(r)

    print("\n── Averages ─────────────────────────────────────────────────")
    ranked = sorted(
        by_model.items(),
        key=lambda kv: -sum(r.total_score for r in kv[1]) / len(kv[1]),
    )
    for model, rs in ranked:
        avg_total = sum(r.total_score for r in rs) / len(rs)
        avg_speed = sum(r.speed_ms for r in rs) // len(rs)
        tier = model_info(model).tier if model_info(model) else "?"
        print(
            f"  {display_name(model):<28} avg={avg_total:.1f}  "
            f"avg_speed={avg_speed}ms  tier={tier}  n={len(rs)}"
        )


def resolve_models(args) -> list[str]:
    if args.models:
        return [m.strip() for m in args.models.split(",") if m.strip()]
    if args.tier == "free":
        ids = configured_models("free") or FREE_MODELS
    elif args.tier == "cheap":
        ids = configured_models("cheap") or CHEAP_MODELS
    elif args.tier == "paid":
        ids = configured_models("paid") or PAID_MODELS
    else:
        # default: cheap (free + cheap) so a fresh clone doesn't torch a credit card
        ids = configured_models("cheap")
        if not ids:
            ids = configured_models("all") or list(AVAILABLE_MODELS)
    return ids


def resolve_judges(args) -> list[str]:
    if args.judges:
        return [j.strip() for j in args.judges.split(",") if j.strip()]
    if args.judge:
        return [args.judge]
    return [pick_default_judge()]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="mager-bench: coding model benchmark (free-tier friendly)"
    )
    parser.add_argument(
        "--models",
        default=None,
        help="comma-separated model IDs (default: configured free+cheap)",
    )
    parser.add_argument(
        "--tier",
        choices=["free", "cheap", "paid", "all"],
        default="cheap",
        help="model tier when --models not set (default: cheap = free+haiku+mini)",
    )
    parser.add_argument("--challenge", default=None, help="run a single challenge by name")
    parser.add_argument(
        "--judge",
        default=None,
        help=f"single judge model ID (default: free pick, e.g. {DEFAULT_JUDGE_MODEL})",
    )
    parser.add_argument(
        "--judges",
        default=None,
        help="comma-separated judges — scores are averaged (reduces single-model bias)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="repeat each model×challenge N times and report mean ± stddev",
    )
    parser.add_argument("--serial", action="store_true", help="run one job at a time")
    parser.add_argument("--output", default=None, help="save results to JSON file")
    parser.add_argument("--list-models", action="store_true", help="list models + key status")
    parser.add_argument("--list-challenges", action="store_true", help="list challenges")
    args = parser.parse_args()

    if args.list_models:
        print(list_models_report())
        return

    if args.list_challenges:
        for c in load_challenges(None):
            print(f"  {c.name}: {c.description}")
        return

    models = resolve_models(args)
    judges = resolve_judges(args)
    runs = max(1, args.runs)
    challenge_names = [args.challenge] if args.challenge else None

    print("mager-bench")
    print(f"  models : {', '.join(models)}")
    print(f"  judges : {', '.join(judges)}")
    print(f"  runs   : {runs}")
    print(f"  mode   : {'serial' if args.serial else 'parallel'}")
    unpaid = [m for m in PAID_MODELS if m not in models]
    if unpaid:
        print(f"  unpaid : {', '.join(unpaid)}  → fund at /fund to unlock")

    results = run_benchmark(
        models, challenge_names, judges, serial=args.serial, runs=runs
    )
    print_table(results, judges, runs)

    if args.output:
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "judge": "+".join(judges),
            "judges": judges,
            "runs": runs,
            "tier": args.tier,
            "results": [asdict(r) for r in results],
        }
        Path(args.output).write_text(json.dumps(payload, indent=2))
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
