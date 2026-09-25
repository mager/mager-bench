"""
mager-bench — rates coding models on correctness, code quality, docs, and speed.

Usage:
    python bench.py                            # subscription subjects and judge through Codex CLI
    python bench.py --tier free --judge gemini-2.5-flash  # free subjects + judge
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
    is_configured,
    pick_default_judge,
)
from judge import score_response_multi, DEFAULT_JUDGE_MODEL
from challenges import load_challenges
from instrumentation import setup_tracing, flush_tracing, get_tracer


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
    # Arize trace id for this run's CHAIN span ("" when tracing is off)
    trace_id: str = ""
    # populated when --runs > 1 after aggregation
    runs: int = 1
    stddev: float | None = None
    scores_per_run: list[float] = field(default_factory=list)
    # full per-run paper trail: every run's response + scores survives
    # aggregation so each trace stays inspectable on the dashboard
    run_details: list[dict] = field(default_factory=list)


def run_model_on_challenge(
    challenge,
    model_id: str,
    judges: list[str],
    run: int = 1,
    thinking_budget: int | None = None,
    reasoning_effort: str | None = None,
    thinking_headroom: int = 32768,
    gateway_timeout: float = 1800,
    judge_max_tokens: int = 2048,
) -> tuple[Result | None, str]:
    provider = get_provider(model_id, thinking_budget=thinking_budget,
                            reasoning_effort=reasoning_effort,
                            thinking_headroom=thinking_headroom,
                            gateway_timeout=gateway_timeout)
    if not provider:
        return None, f"{model_id}: no API key configured, skipping"

    # One CHAIN span per model×challenge run; auto-instrumented LLM calls
    # (subject + judge) nest under it. No-op when tracing isn't configured.
    with get_tracer().start_as_current_span(f"bench.{challenge.name}") as span:
        span.set_attribute("openinference.span.kind", "CHAIN")
        span.set_attribute("input.value", challenge.prompt)
        span.set_attribute("metadata.model", model_id)
        span.set_attribute("metadata.challenge", challenge.name)
        span.set_attribute("metadata.run", run)
        span_ctx = span.get_span_context()
        trace_id = f"{span_ctx.trace_id:032x}" if span_ctx.is_valid else ""

        t0 = time.perf_counter()
        try:
            response = provider.complete(challenge.prompt, max_tokens=challenge.max_tokens)
        except Exception as e:
            span.set_attribute("error.message", str(e))
            return None, f"{model_id}: ERROR: {e}"
        elapsed_ms = int((time.perf_counter() - t0) * 1000)

        scores = score_response_multi(challenge, response, model_id, judges,
                                        judge_max_tokens=judge_max_tokens)
        span.set_attribute("output.value", response)
        span.set_attribute("metadata.correctness", scores["correctness"])
        span.set_attribute("metadata.quality", scores["quality"])
        span.set_attribute("metadata.documentation", scores["documentation"])
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
        trace_id=trace_id,
        runs=1,
        scores_per_run=[total],
        run_details=[
            {
                "run": run,
                "correctness": scores["correctness"],
                "quality": scores["quality"],
                "documentation": scores["documentation"],
                "total": total,
                "speed_ms": elapsed_ms,
                "notes": scores.get("notes", ""),
                "response": response,
            }
        ],
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
        group_sorted = sorted(group, key=lambda x: x.run)
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
                trace_id=best.trace_id,
                runs=len(group),
                stddev=std,
                scores_per_run=totals,
                run_details=[d for g in group_sorted for d in g.run_details],
            )
        )
    return out


def run_benchmark(
    models: list[str],
    challenge_names: list[str] | None,
    judges: list[str],
    serial: bool = False,
    runs: int = 1,
    thinking_budget: int | None = None,
    reasoning_effort: str | None = None,
    thinking_headroom: int = 32768,
    gateway_timeout: float = 1800,
    judge_max_tokens: int = 2048,
) -> list[Result]:
    challenges = load_challenges(challenge_names)
    results: list[Result] = []

    for challenge in challenges:
        print(f"\n── {challenge.name} ──────────────────────────────────")
        jobs: list[tuple[str, int]] = [
            (m, run) for run in range(1, runs + 1) for m in models
        ]

        def _run(model_id: str, run: int) -> tuple[Result | None, str]:
            return run_model_on_challenge(
                challenge, model_id, judges, run,
                thinking_budget=thinking_budget,
                reasoning_effort=reasoning_effort,
                thinking_headroom=thinking_headroom,
                gateway_timeout=gateway_timeout,
                judge_max_tokens=judge_max_tokens,
            )

        if serial:
            for model_id, run in jobs:
                result, line = _run(model_id, run)
                print(f"  {line}")
                if result:
                    results.append(result)
        else:
            workers = min(8, max(1, len(jobs)))
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {
                    pool.submit(_run, m, run): (m, run)
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
    elif args.tier == "subscription":
        ids = configured_models("subscription")
    else:
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
        description="mager-bench: coding model benchmark (ChatGPT subscription by default)"
    )
    parser.add_argument(
        "--models",
        default=None,
        help="comma-separated model IDs (default: configured subscription models)",
    )
    parser.add_argument(
        "--tier",
        choices=["free", "cheap", "paid", "subscription", "all"],
        default="subscription",
        help="model tier when --models not set (default: subscription via Codex CLI)",
    )
    parser.add_argument(
        "--challenge",
        default=None,
        help="comma-separated challenge names (default: all)",
    )
    parser.add_argument(
        "--judge",
        default=None,
        help=f"single judge model ID (default: {DEFAULT_JUDGE_MODEL}, ChatGPT subscription)",
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
    parser.add_argument("--serial", action="store_true", help="run one job at a time (subscription default)")
    parser.add_argument("--parallel", action="store_true", help="allow concurrent subscription subject calls")
    parser.add_argument("--allow-api", action="store_true",
                        help="explicitly allow paid/free API or gateway calls instead of subscription-only Codex CLI")
    parser.add_argument("--output", default=None, help="save results to JSON file")
    parser.add_argument("--rescore-file", default=None,
                        help="rescore saved single-run responses without generating them again")
    parser.add_argument("--list-models", action="store_true", help="list models + key status")
    parser.add_argument("--list-challenges", action="store_true", help="list challenges")
    parser.add_argument(
        "--thinking-budget", type=int, default=None,
        help="cap Anthropic thinking tokens per call (default: uncapped; "
             "2048 is plenty for subjects — uncapped burned $0.08/call live)",
    )
    parser.add_argument(
        "--reasoning-effort", default=None, choices=["low", "medium", "high"],
        help="cap subject reasoning for OpenAI and AI Gateway models (default: model default; "
             "low/medium tames GLM's 7–9k thinking blowups)",
    )
    parser.add_argument(
        "--judge-max-tokens", type=int, default=16384,
        help="judge output-length target (default: 16384; CLI treats this as an instruction)",
    )
    parser.add_argument(
        "--thinking-headroom", type=int, default=32768,
        help="extra tokens above challenge max_tokens for thinking models "
             "on the gateway (default: 32768 — live-tested; doom/slots starve "
             "without it. Billed only on actual use)",
    )
    parser.add_argument(
        "--gateway-timeout", type=float, default=1800,
        help="seconds before a gateway call is abandoned (default: 1800 — "
             "big-build streams run 5–10+ min, SDK default 600 decapitates them)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="print what would run (models × challenges × runs, tiers, judges) "
             "and exit without spending a token",
    )
    args = parser.parse_args()

    if args.output and Path(args.output).resolve() == Path(__file__).resolve().parent / "results.json":
        parser.error("save runs under runs/ and merge them; --output results.json would erase the board")

    if args.list_models:
        print(list_models_report())
        return

    if args.list_challenges:
        for c in load_challenges(None):
            print(f"  {c.name}: {c.description}")
        return

    if args.rescore_file:
        if not args.output or Path(args.output).resolve() == Path(args.rescore_file).resolve():
            parser.error("--rescore-file requires a different --output path")
        payload = json.loads(Path(args.rescore_file).read_text())
        if payload.get("runs") != 1:
            parser.error("--rescore-file currently supports only single-run files")
        old_judges = payload.get("judges") or [payload["judge"]]
        if args.judge or args.judges:
            parser.error("--rescore-file reuses the saved judge; omit --judge/--judges")
        missing = [judge_id for judge_id in old_judges if not is_configured(judge_id)]
        if missing and not args.dry_run:
            parser.error(f"judge(s) not configured: {', '.join(missing)}")
        if not args.dry_run and not args.allow_api and any(
            model_info(judge_id).family != "codex-cli" for judge_id in old_judges
        ):
            parser.error("API judging requires --allow-api; subscription-only is the default")
        selected = ({name.strip() for name in args.challenge.split(",")}
                    if args.challenge else {row["challenge"] for row in payload["results"]})
        challenges = {challenge.name: challenge for challenge in load_challenges(None)}
        rows = [row for row in payload["results"] if row["challenge"] in selected]
        if selected - {row["challenge"] for row in rows}:
            parser.error("--challenge includes a challenge missing from --rescore-file")
        print(f"rescore: {len(rows)} saved responses × {len(old_judges)} judges "
              f"= {len(rows) * len(old_judges)} judge calls")
        if args.dry_run:
            return
        for row in rows:
            scores = score_response_multi(challenges[row["challenge"]], row["response"],
                                          row["model"], old_judges,
                                          judge_max_tokens=args.judge_max_tokens)
            if "judge error" in scores.get("notes", "").lower():
                raise RuntimeError(f"judge failed for {row['challenge']}; no file written")
            total = round((scores["correctness"] + scores["quality"] +
                           scores["documentation"]) / 3, 1)
            row.update({key: scores[key] for key in
                        ("correctness", "quality", "documentation", "notes", "judge")})
            row["total_score"] = total
            row["scores_per_run"] = [total]
            if row.get("run_details"):
                row["run_details"][0].update({
                    "correctness": scores["correctness"], "quality": scores["quality"],
                    "documentation": scores["documentation"], "notes": scores["notes"],
                    "total": total,
                })
            print(f"  {row['challenge']}: {total:.1f} — {scores['notes']}")
        payload["generated_at"] = datetime.now(timezone.utc).isoformat()
        payload["rescore_source"] = args.rescore_file
        Path(args.output).write_text(json.dumps(payload, indent=2))
        print(f"Rescored results saved to {args.output}")
        return

    models = resolve_models(args)
    judges = resolve_judges(args)
    if not models:
        parser.error("no subscription models configured; install Codex CLI and run `codex login`")
    if args.serial and args.parallel:
        parser.error("choose either --serial or --parallel")
    if not args.dry_run and not args.allow_api and any(
        model_info(model_id) is None or model_info(model_id).family != "codex-cli"
        for model_id in models + judges
    ):
        parser.error("API or gateway models require --allow-api; subscription-only is the default")
    if not args.dry_run:
        missing_judges = [j for j in judges if not is_configured(j)]
        if missing_judges:
            parser.error(f"judge(s) not configured: {', '.join(missing_judges)}; "
                         "sign in with `codex login` for subscription runs.")
    runs = max(1, args.runs)
    serial = args.serial or (not args.parallel and all(
        model_info(model_id) and model_info(model_id).family == "codex-cli"
        for model_id in models
    ))
    challenge_names = (
        [c.strip() for c in args.challenge.split(",") if c.strip()]
        if args.challenge
        else None
    )

    print("mager-bench")
    if args.allow_api:
        setup_tracing()
    else:
        print("  tracing: disabled for subscription-only runs")
    print(f"  models : {', '.join(models)}")
    print(f"  judges : {', '.join(judges)}")
    print(f"  runs   : {runs}")
    print(f"  mode   : {'serial' if serial else 'parallel'}")
    if args.thinking_budget:
        print(f"  thinking-budget : {args.thinking_budget}")
    if args.reasoning_effort:
        print(f"  reasoning-effort: {args.reasoning_effort}")
    print(f"  thinking-headroom : {args.thinking_headroom}")
    print(f"  gateway-timeout   : {int(args.gateway_timeout)}s")
    print(f"  judge-max-tokens: {args.judge_max_tokens}")
    unpaid = [m for m in PAID_MODELS if m not in models]
    if args.allow_api and unpaid:
        print(f"  unpaid : {', '.join(unpaid)}  → fund at /fund to unlock")

    if args.dry_run:
        challenges = load_challenges(challenge_names)
        total_calls = len(challenges) * len(models) * runs
        total_judges = total_calls * len(judges)
        tiers = sorted({model_info(m).tier if model_info(m) else "?" for m in models})
        judge_tiers = sorted({model_info(j).tier if model_info(j) else "?" for j in judges})
        print(f"\n  dry-run: {len(models)} models × {len(challenges)} challenges "
              f"× {runs} runs = {total_calls} subject calls + "
              f"{total_judges} judge calls (subject tiers: {', '.join(tiers)}; "
              f"judge tiers: {', '.join(judge_tiers)})")
        print("  no model calls made.")
        return

    results = run_benchmark(
        models, challenge_names, judges, serial=serial, runs=runs,
        thinking_budget=args.thinking_budget,
        reasoning_effort=args.reasoning_effort,
        thinking_headroom=args.thinking_headroom,
        gateway_timeout=args.gateway_timeout,
        judge_max_tokens=args.judge_max_tokens,
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

    flush_tracing()  # CLI app: ship buffered spans before exit


if __name__ == "__main__":
    main()
