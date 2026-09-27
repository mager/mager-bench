"""Subscription-only Counterexample Lab runner; separate from the original board."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from counterexample_lab.grader import VERSION, SubmissionError, grade

ROOT = Path(__file__).resolve().parent
PROMPT = ROOT / "counterexample_lab/prompt.md"
RUNS = ROOT / "runs/v1.1"


def suite_fingerprint() -> str:
    """Hash the exact contract, oracle, scorer, and runner used for this run."""
    digest = hashlib.sha256()
    for name in ("counterexample_lab/prompt.md", "counterexample_lab/ledger.py",
                 "counterexample_lab/grader.py", "bench_v1_1.py", "providers.py"):
        digest.update(name.encode() + b"\0" + (ROOT / name).read_bytes() + b"\0")
    return digest.hexdigest()


def output_path(value: str) -> Path:
    path = Path(value).resolve()
    if not path.is_relative_to(RUNS.resolve()) or path.suffix != ".json":
        raise ValueError("v1.1 artifacts must be JSON files under runs/v1.1/")
    if path.exists():
        raise ValueError("output already exists; preserve prior attempts with a new filename")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--model", help="subscription subject, e.g. codex-cli/gpt-6-astra")
    source.add_argument("--submission", type=Path, help="grade a saved JSON answer without model calls")
    parser.add_argument("--reasoning-effort", default="low",
                        choices=["low", "medium", "high", "xhigh", "max", "ultra"])
    parser.add_argument("--output", help="new artifact under runs/v1.1/ (required except dry-run)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if not args.dry_run and not args.output:
        parser.error("--output is required to retain every attempt")
    try:
        destination = output_path(args.output) if args.output else None
    except ValueError as exc:
        parser.error(str(exc))

    if args.model:
        from providers import get_provider, is_configured, model_info
        info = model_info(args.model)
        if info is None or info.family != "codex-cli":
            parser.error("only registered codex-cli/ subscription models are supported")
    if args.submission and not args.submission.is_file():
        parser.error("submission file does not exist")
    print(f"mager-bench {VERSION} / Counterexample Lab")
    print(f"planned: {1 if args.model else 0} subject calls + 0 judge calls")
    print("scoring: deterministic mutation coverage; separate from results.json")
    if args.dry_run:
        print("dry-run: no model calls made")
        return 0

    payload = {
        "benchmark_version": VERSION,
        "challenge": "counterexample-ledger",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "suite_sha256": suite_fingerprint(),
        "prompt": PROMPT.read_text(),
        "source": "subscription" if args.model else "offline",
        "model": args.model,
        "reasoning_effort": args.reasoning_effort if args.model else None,
        "output_token_target": 4096 if args.model else None,
        "response": "",
        "status": "failed",
        "score": None,
    }
    started = time.perf_counter()
    # Only transport/format failures are unscored. Oracle/scorer exceptions
    # propagate rather than masquerading as model failures or zero coverage.
    failure = None
    if args.model:
        try:
            if not is_configured(args.model):
                raise RuntimeError("ChatGPT CLI login unavailable; run codex login status")
            provider = get_provider(args.model, reasoning_effort=args.reasoning_effort)
            if provider is None:
                raise RuntimeError("subscription provider unavailable")
            payload["response"] = provider.complete(payload["prompt"], max_tokens=4096)
        except Exception as exc:
            failure = f"provider error: {exc}"
    else:
        try:
            payload["response"] = args.submission.read_text()
        except (OSError, UnicodeError) as exc:
            failure = f"submission read error: {exc}"
    payload["subject_elapsed_ms"] = round((time.perf_counter() - started) * 1000)
    if failure is None:
        try:
            payload["score"] = grade(payload["response"])
        except SubmissionError as exc:
            failure = str(exc)
    if failure is None:
        payload["status"] = "completed"
    else:
        payload["error"] = failure
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x") as output:
        json.dump(payload, output, indent=2, allow_nan=False)
        output.write("\n")
    print(f"artifact: {destination}")
    if failure:
        print(f"unscored failed call: {failure}", file=sys.stderr)
        return 1
    score = payload["score"]
    print(f"exposed {score['killed']}/{score['total_mutants']} faults; "
          f"{score['valid_traces']}/{score['total_traces']} traces match the oracle")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
