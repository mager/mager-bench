# mager-bench 1.2

A fast benchmark of useful JavaScript programs: split a bill, clean a contact
CSV, and find a meeting time. Each task has twelve public cases with literal
expected outputs. There are three subject calls, zero model judges, no retries,
and 36 equally weighted checks. This is an agent-harness benchmark, not a direct
model API latency test.

## What makes it difficult

- **Split a bill:** weighted shares, largest-remainder cent allocation, stable
  tie-breaking, nonparticipating payers, refunds, and deterministic settlement.
- **Clean a CSV:** quoted commas and multiline fields, escaped quotes, BOMs,
  reordered headers, malformed records, email normalization, duplicate contact
  merging, stable tag order, and rejection counts.
- **Find a meeting:** time zone offsets, overlapping and adjacent work periods,
  split days, expanded busy intervals, grid alignment, and midnight boundaries.

The exact contracts and all public cases live in `everyday_v1_2/tasks.py`.
The examples shown on the website are expected outputs, never model outputs.
Fixture programs in `tests/fixtures/v1_2/` validate the grader; they are written
by the benchmark author and are never submitted as model results.

## Speed and effort

Always use the **lowest supported reasoning effort** for each model. The runner
reads the local Codex model catalog, picks the least effort in the advertised
list, and records that list and the selected value. Unknown metadata fails
closed. GPT-6 Sol currently lists `low` as its lowest setting. There is no
higher-effort CLI override. Availability is a separate check; a catalog entry
does not prove the subscription can run that model.

Each generation call has a 90-second deadline and a prompted output target of
3,072 tokens, not an API-enforced cap. Calls are sequential (up to 270 seconds
of provider waiting). The runner stops on the first provider/format failure.
It does not retry or switch models. Programs are checked locally in fresh
QuickJS contexts with 16 MiB memory, a 256 KiB stack, and a 100 ms CPU limit per
case. No filesystem, process, Python callback, or network bindings are exposed.
This is a bounded interpreter, not a general-purpose OS sandbox or a claim of
protection from interpreter vulnerabilities. Standard synchronous JavaScript
only. No Node globals or packages. QuickJS is pinned at 1.19.4.

## Scoring and evidence

A check passes only when the returned JSON structurally matches the literal
expected result. Object property order is ignored; arrays are ordered; boolean
and numeric values are distinct. Code exceptions, invalid JavaScript, timeout,
non-JSON return values, and memory exhaustion fail affected checks. Empty or
oversized responses and provider errors are unscored. A fenced JS answer is
accepted if the fence encloses the complete answer. Source is limited to 64 KiB.

The overall count is published only after all three submissions are scored.
Partial task results remain in the artifact if a later call fails, but the
attempt has no overall score. Save before calls and after every task. Interrupts
retain an unscored artifact. Never overwrite an existing attempt.

The SHA-256 fingerprint includes contracts, cases, grader, runner, frozen
provider implementation, and dependency manifest. The exporter checks prompts,
effort policy, budgets, statuses, and fingerprints and regrades completed
submissions. Historical v1.1 and legacy results are separate. These 36 public
checks are neither exhaustive nor hidden; they measure this small contract
sample and are vulnerable to memorization. One attempt cannot establish a
reliable model ranking. Timings include harness overhead and account conditions.

## Run and publish

```sh
.venv/bin/python -m pip install -r requirements-v1.2.txt
codex login status
.venv/bin/python bench_v1_2.py --model codex-cli/gpt-6-sol --dry-run
.venv/bin/python bench_v1_2.py --model codex-cli/gpt-6-sol \
  --output runs/v1.2/YYYY-MM-DD-gpt-6-sol-r1.json
.venv/bin/python web/scripts/sync-everyday-data.py
.venv/bin/python -m unittest discover -s tests
npm --prefix web run lint
npm --prefix web run build
cd web
vercel --prod --yes
```

Use ChatGPT login only. No API or gateway fallback. Keep source, run artifacts,
and generated `web/data/everyday.json` together in the commit, then push. Never
merge this suite into `results.json` or call the legacy merge script on it.

## First attempt: October 2, 2026

GPT-6 Sol was requested as the first subject. Both the availability smoke check
and first benchmark call were rejected by Codex CLI 0.154.0 with:
`The 'gpt-6-sol' model is not supported when using Codex with a ChatGPT account.`
The model produced no answer and has no score. The first task failed; the other
two were not called. Evidence is in `runs/v1.2/2026-10-02-gpt-6-sol-r1.json` and
`runs/v1.2/preflight/2026-10-02-gpt-6-sol.json`. No substitute model was run.

Version 1.1's Counterexample Lab is frozen and archived. The next substantive
change to this v1.2 contract, case corpus, scoring, or budgets requires a new
version; do not quietly change a published score's meaning.
