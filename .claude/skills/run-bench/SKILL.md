---
name: run-bench
description: Run the active mager-bench 1.1 Counterexample Lab through the ChatGPT subscription.
---

# Run mager-bench 1.1

Follow `/bench` in `.opencode/commands/bench.md` and the board rules in
`AGENTS.md`; `/bench` wins if these instructions differ.

The active entrypoint is `bench_v1_1.py`, with ChatGPT-signed-in `codex-cli/`
subjects and zero judge-model calls. Read `docs/mager-bench-1.1.md`. Check
`codex login status`, dry-run, and smoke-test a new model before its first run.
Save every attempt under `runs/v1.1/` with a fresh filename. Inspect the raw
response, suite hash, effort, trace validity, and mutation coverage. Failed calls
remain unscored; preserve them when rerunning. Calibration requires repeated
samples with matching effort and suite hashes before publishing a ranking.

Do not merge 1.1 artifacts into the legacy board. `bench.py` preserves the
original thirteen tasks, including archived FizzBuzz, binary search, and
refactor. For explicit legacy reproduction/publication only, follow the legacy
section of `/bench`: the judge remains `codex-cli/gpt-5.6-sol`, and the full
13-row run is validated, merged, synced, deployed, committed, and pushed.
No API fallback and no invented scores belong in either workflow.
