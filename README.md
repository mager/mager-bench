# mager-bench

A personal coding-model benchmark: thirteen tasks from FizzBuzz to a one-file Doom-style raycaster, scored on correctness, code quality, and documentation. Each score links to the answer and the judge's notes.

**Live board:** [bench.mager.co](https://bench.mager.co)

**Original Sonnet 5 board:** [archive](https://bench.mager.co/archive/sonnet-5)

**Current board JSON:** [`/api/results`](https://bench.mager.co/api/results)

## ChatGPT subscription workflow

All new benchmark calls run through fresh, read-only headless Codex CLI sessions signed in to a local ChatGPT subscription. The default subjects are `codex-cli/gpt-5.6-sol` and `codex-cli/gpt-6-astra`; the single board judge is `codex-cli/gpt-5.6-sol`. GPT-6 Sol itself was not available through this account's Codex CLI on 2026-09-25, so the earlier GPT-6 Sol API default has been retired.

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

## Challenges

| Name | What it tests |
|---|---|
| `fizzbuzz` | Baseline correctness and style |
| `binary-search` | Algorithm and full documentation |
| `api-client` | Class design, errors, type hints, docs |
| `readme-writer` | Documentation ability |
| `refactor` | Code clarity and change explanation |
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
