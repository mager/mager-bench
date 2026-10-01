# mager-bench 1.1: Counterexample Lab

Status: first preliminary calibration published, with three fresh attempts per
model. Counterexample Lab is the active 1.1 track. See the
[calibration protocol](../runs/v1.1/2026-09-30-calibration.md) and
[public evidence](https://bench.mager.co/runs).

We retire `fizzbuzz`, `binary-search`, and `refactor` from the current suite.
Their prompts, responses, and scores remain in the frozen **legacy-13** suite
for reproduction; `bench.py` still runs that original contract. The other ten
legacy tasks remain available as optional baselines, outside the 1.1 score.
See the [retirement note](archive/easy-tests.md) and
[suite manifest](../benchmark-suites.json). Historical results keep their
original identities and are never mixed with the new track's scores.

## Why change the test?

The saved Astra run averages 9.2769 across thirteen tasks, displayed as 9.3. Four
task totals are perfect. Those scores combine correctness, code quality, and
documentation under the `codex-cli/gpt-5.6-sol` judge. One run cannot establish a
ceiling, but it gives us a reason to investigate whether the tasks still separate
strong models meaningfully.

Counterexample Lab asks the model to design a small regression suite for a
stateful system. A successful answer must predict exact behavior and expose
distinct implementation faults within a tight budget. Longer code or persuasive
explanations do not earn points.

## The task

The model receives a ledger contract and returns JSON containing at most four
traces and at most twelve events **across all traces**. Each trace includes the
expected output of every event. Each starts fresh: accounts `a`, `b`, and `c`
hold 10, 0, and 0 units respectively; all revisions are zero; the request cache
is empty.

The operations are transfer, inspect, and restart. A transfer names a request
ID, source account, destination account, amount, and expected source revision.
Successful transfers move money atomically and increment both account
revisions. Inspect exposes the observable account state. Restart preserves
committed state and the request cache. It models a durable reload after
completed operations; it does not test disk writes, interrupted commits, or
real crash recovery.

Request caching makes the problem stateful. A transfer's fingerprint includes
all its fields except the request ID. Cache lookup happens before validation:
an identical retry returns the cached result, and reuse of the ID with a changed
payload returns a conflict while preserving the original cache entry. Failed
transfers are cached too. New requests check errors in this order:
`unknown_account`, `same_account`, `stale_revision`, `insufficient_funds`.

The [model prompt](../counterexample_lab/prompt.md) is the authoritative source
for the JSON schema, input limits, and exact output fields. The
[implementation](../counterexample_lab/) defines the reference ledger and its
faults; the [runner](../bench_v1_1.py) accepts either a model call or a saved
submission.

## What earns credit?

The deterministic grader first checks a trace's expected outputs against the
reference implementation. Only a trace with correct expectations can expose a
fault. It then replays that trace against eight isolated broken variants:

| Variant | Fault |
|---|---|
| `forget_cache_on_restart` | Drops request history on restart |
| `cache_success_only` | Forgets failed requests |
| `ignore_conflicting_payload` | Treats changed payloads as identical retries |
| `revalidate_duplicate` | Checks a retry against current state again |
| `debit_before_credit_validation` | Debits the source before rejecting an unknown destination |
| `no_destination_revision` | Omits the destination's revision increment |
| `accept_stale_revision` | Accepts a stale source revision |
| `conflict_overwrites_cache` | Replaces the original cache entry on conflict |

A fault is “killed” when a correct trace produces different observable outputs
under that variant. Each fault counts once, however many traces detect it. The
primary result is **faults killed / 8**, accompanied by **oracle-correct traces /
submitted traces**. A well-formed submission whose expectations are all wrong
scores zero. Empty responses, malformed submissions, and provider failures are
unscored failures and must be resolved before publishing comparisons.

The grader interprets submitted data; it never executes model-authored code.
It makes no LLM judge calls. Determinism removes judge taste from this track,
but does not prove that the reference or fault selection is correct. Repository
tests and independent review remain part of validating the benchmark itself.

## Run protocol

Use the existing local ChatGPT subscription provider. No API fallback belongs
in this track. Check authentication and smoke-test any new model before running:

```bash
codex login status
.venv/bin/python -c "from providers import get_provider; print(get_provider('codex-cli/gpt-6-astra').complete('Say OK'))"
.venv/bin/python bench_v1_1.py --model codex-cli/gpt-6-astra \
  --reasoning-effort low --dry-run
.venv/bin/python bench_v1_1.py --model codex-cli/gpt-6-astra \
  --reasoning-effort low \
  --output runs/v1.1/YYYY-MM-DD-codex-cli-gpt-6-astra.json
```

To grade an existing answer without model calls:

```bash
.venv/bin/python bench_v1_1.py --submission path/to/submission.json \
  --output runs/v1.1/offline-check.json
```

Keep these artifacts separate from `results.json` and the old board's merge
workflow. Save the raw response, model identity, reasoning effort, timing, and
the combined suite hash with each run. The CLI's output-length instruction is
not a hard API token cap; this remains an agent-harness benchmark.

## Calibration and versions

The hypothesis is that compact suites requiring exact state tracking will be
harder than familiar implementation prompts. Test that with multiple independent
samples per model, a frozen specification, the same reasoning effort, and
reported failure counts and score distributions. Astra helping design the task
is not evidence of its performance on it.

The September 30 calibration used low reasoning effort for both models. Astra
exposed 7/8 faults in each of three attempts; Sol exposed 7/8, 6/8, and 5/8.
Every trace matched the oracle. Neither model exposed partial-transfer mutation
in these attempts. This small sample is preliminary, not a general ranking.

The code and faults are public. This release is not a secret holdout or a claim
of resistance to future training contamination. Eight faults may themselves
prove too easy; calibration should tell us before we expand the suite.

Use simple release numbers. The next substantive change to the contract, fault
corpus, budget, or scoring becomes **1.2**. Preserve old artifacts and their
hashes; do not rename historical scores or compare different contracts as one
leaderboard.
