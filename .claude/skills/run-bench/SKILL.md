---
name: run-bench
description: Run and publish a model on the mager-bench subscription leaderboard.
---

# Run a bench and publish it

Follow `/bench` in `.opencode/commands/bench.md` and the board rules in
`AGENTS.md`; `/bench` wins if these instructions differ.

Use the ChatGPT-signed-in `codex-cli/` providers for all new subject and judge
calls. The default judge is `codex-cli/gpt-5.6-sol`. Check `codex login status`,
smoke-test the subject, and run `bench.py --dry-run` before the full suite.
Save the run under `runs/`, verify every row, merge with
`node web/scripts/merge-subscription-run.mjs <run-file>`, sync the web data,
deploy, then commit and push the run and generated board. Never mix judges or
publish a `judge error` as a score. API or gateway calls require `--allow-api`
and are outside the current board.
