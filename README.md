# mager-bench

A personal coding-model benchmark. **Version 1.1 introduces Counterexample Lab:**
write compact regression tests that expose eight faults in a stateful ledger.
The grader executes the submitted traces and checks their exact expected results.

[1.1 specification](docs/mager-bench-1.1.md) ·
[Short announcement draft](posts/2026-09-26-mager-bench-1.1.md) ·
[Archived easy tests](docs/archive/easy-tests.md)

FizzBuzz, binary search, and the tiny refactor task are retired from the new
suite. The original thirteen-task board and prompts remain available for
reproduction. Its scores average correctness, quality, and documentation;
they are not comparable to 1.1's mutation coverage. No 1.1 model scores have
been published yet.

```bash
.venv/bin/python bench_v1_1.py --model codex-cli/gpt-6-astra --dry-run
# Check codex login status and smoke-test a new model before its first run.
.venv/bin/python bench_v1_1.py --model codex-cli/gpt-6-astra \
  --reasoning-effort low --output runs/v1.1/YYYY-MM-DD-codex-cli-gpt-6-astra.json
```

Version 1.1 uses the local ChatGPT subscription for subjects and a deterministic
grader with zero judge-model calls. Save every attempt separately under
`runs/v1.1/`; these artifacts do not go through the legacy board's merge script.
The [suite manifest](benchmark-suites.json) records active and retired tasks.

**Legacy thirteen-task board:** [bench.mager.co](https://bench.mager.co)

**Original Sonnet 5 board:** [archive](https://bench.mager.co/archive/sonnet-5)

**Current board JSON:** [`/api/results`](https://bench.mager.co/api/results)

## Legacy thirteen-task reproduction

Legacy benchmark calls run through fresh, read-only headless Codex CLI sessions signed in to a local ChatGPT subscription. The default subjects are `codex-cli/gpt-5.6-sol` and `codex-cli/gpt-6-astra`; the single legacy board judge is `codex-cli/gpt-5.6-sol`. GPT-6 Sol itself was not available through this account's Codex CLI on 2026-09-25, so the earlier GPT-6 Sol API default has been retired.

The CLI receives an instruction to target each challenge's output length, but does not impose the API's hard output-token cap. This is an agent-harness benchmark. Sol judging its own answers is a possible source of bias. We preserve the earlier Sonnet 5 API board separately rather than mix judges in one ranking.

```bash
# Install requirements in .venv, then sign the Codex CLI in to ChatGPT.
codex login status

# Dry-run first: this prints models × challenges × runs and judge calls.
.venv/bin/python bench.py --dry-run

# Smoke-test a new model before its full suite.
.venv/bin/python -c "from providers import get_provider; print(get_provider('codex-cli/gpt-6-astra').complete('Say OK'))"

# Run one model and save the full paper trail.
.venv/bin/python bench.py --models codex-cli/gpt-6-astra --serial \
  --reasoning-effort low --output runs/YYYY-MM-DD-codex-cli-gpt-6-astra.json

# Validate and merge its rows into the subscription board, then update web data.
node web/scripts/merge-subscription-run.mjs runs/YYYY-MM-DD-codex-cli-gpt-6-astra.json
node web/scripts/sync-results.mjs
```

Never write a model run directly to `results.json`. The merge script requires all 13 challenges, full responses, one judge, and valid scores. A failed subject or judge call is a crash to rerun, not a score of zero. `/bench` in opencode is the canonical publish workflow, with the detailed rules in `AGENTS.md`.

The older API providers remain in code for reproducibility, but a new API or gateway run requires explicit `--allow-api` and cannot be merged into the current subscription board. The former API funding drive is archived.

## Using Pro to judge other models

The ChatGPT subscription covers the GPT calls made through the signed-in Codex CLI. It does not provide Claude, Gemini, GLM, or other providers' inference through Codex. Those subjects need their own provider or a local runtime; their saved answers can then be graded by the subscription-backed GPT judge.

The harness already supports an explicitly opted-in external subject with the Codex judge, saving the result separately:

```bash
.venv/bin/python bench.py --models <external-model-id> \
  --judge codex-cli/gpt-5.6-sol --allow-api --serial --dry-run
```

Remove `--dry-run` and add an output path under `runs/` to execute it. This makes external subject calls and is outside the current subscription-only run policy. The subscription board's merge script rejects those runs.

For the archived board, we can reuse the original answers without making new subject calls. A migration must grade every saved run with GPT, recompute multi-run averages and variance, and record the new judge separately from the original Sonnet verdicts. The existing `--rescore-file` command only handles single-run files and retains their original judge, so it is not yet an archive migration command.

## Legacy challenges

| Name | What it tests |
|---|---|
| `fizzbuzz` | Archived — baseline correctness and style |
| `binary-search` | Archived — algorithm and full documentation |
| `api-client` | Class design, errors, type hints, docs |
| `readme-writer` | Documentation ability |
| `refactor` | Archived — code clarity and change explanation |
| `test-writing` | pytest edge cases and assertions |
| `debug` | Finding and fixing three Python bugs |
| `async-fetch` | Concurrency, timeouts, retries |
| `sql` | CTEs, windows, aggregations |
| `go-test` | Idiomatic Go table-driven tests |
| `elixir-test` | ExUnit tests and Unicode handling |
| `doom` | One-file DDA raycaster game |
| `slots` | One-file slot machine with reels and betting |

Each challenge is scored 0–10 on correctness, quality, and documentation. The displayed total is their mean, rounded to one decimal. Speed is reported but not scored. Single-run variance and model-judge bias mean small score gaps should be treated cautiously.

To add a new subscription model, add a `ModelInfo` with the `codex-cli` family and `subscription` tier in `providers.py`, smoke-test it, then run the full suite under the board's judge. The web app in `web/` is a Next.js dashboard deployed on Vercel.

## License

MIT
