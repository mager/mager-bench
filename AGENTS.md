# mager-bench — agent harness notes

`/bench` in `.opencode/commands/bench.md` is the canonical workflow.
`.claude/skills/run-bench/SKILL.md` mirrors it; if they disagree, `/bench` wins.

## Current run policy

- **Use the local ChatGPT subscription exclusively.** `bench.py` defaults to
  `codex-cli/` subjects and the `codex-cli/gpt-5.6-sol` judge. It does not fall
  back to an API key or gateway. API runs require an explicit `--allow-api` and
  are outside the current published board.
- **GPT-6 Astra is available** as `codex-cli/gpt-6-astra`. GPT-6 Sol is not
  available through this ChatGPT-signed-in CLI account, so do not name it as the
  subscription judge unless a fresh smoke test proves that changed.
- **Dry-run first:** `bench.py --dry-run` prints subject and judge call counts.
  Run `codex login status` and smoke-test each new model with
  `get_provider('<model-id>').complete('Say OK')` before a full run.
- **One judge per board.** The current `results.json` uses
  `codex-cli/gpt-5.6-sol`. The earlier Sonnet 5 board is archived under `runs/`.
  Never mix judge identities or relabel old verdicts.
- **No invented scores.** Empty responses, missing rows, and `judge error`
  notes are failed calls. Resolve and rerun before publishing; do not score
  crashes as zero. Codex CLI receives an output-length instruction rather than
  an API-enforced output cap, so label this an agent-harness benchmark.
- **Merge, don't overwrite.** Save each model run to `runs/YYYY-MM-DD-<model>.json`,
  then run `node web/scripts/merge-subscription-run.mjs <run-file>` to merge its
  13 validated rows into `results.json`. Never pass `--output results.json`.
- **Commit the paper trail.** Commit `results.json`, the source file in `runs/`,
  and generated `web/data/*` together. Publish with
  `node web/scripts/sync-results.mjs`, then `cd web && vercel --prod`, followed
  by `git add -A && git commit && git push`.

## Full-run example

```bash
cd ~/Code/mager-bench
codex login status
.venv/bin/python bench.py --models codex-cli/gpt-6-astra --serial --dry-run
.venv/bin/python bench.py --models codex-cli/gpt-6-astra --serial \
  --reasoning-effort low --output runs/YYYY-MM-DD-codex-cli-gpt-6-astra.json
node web/scripts/merge-subscription-run.mjs runs/YYYY-MM-DD-codex-cli-gpt-6-astra.json
node web/scripts/sync-results.mjs
```
