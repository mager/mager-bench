---
description: Run mager-bench 2.0 through the local ChatGPT subscription
---

# /bench — mager-bench 2.0

Read `docs/mager-bench-2.0.md`. Three small repositories, two work orders each,
192 checks, zero model judges. Always use the lowest supported effort; the
runner selects it from the Codex catalog. No API fallback, model substitution,
or session retries. Codex can retry transport requests internally.

```sh
codex login status
.venv/bin/python bench_v2.py --self-test --level 3
.venv/bin/python bench_v2.py --model codex-cli/<model-id> --smoke --dry-run
.venv/bin/python bench_v2.py --model codex-cli/<model-id> --smoke \
  --output runs/v2/YYYY-MM-DD-<model>-preflight.json
.venv/bin/python bench_v2.py --model codex-cli/<model-id> --seed 42 --level 1 --dry-run
.venv/bin/python bench_v2.py --model codex-cli/<model-id> --seed 42 --level 1 \
  --output runs/v2/YYYY-MM-DD-<model>-seed42-level1-r1.json
.venv/bin/python web/scripts/sync-agent-v2-data.py
.venv/bin/python -m unittest discover -s tests
npm --prefix web run lint
npm --prefix web run build
```

Stop after a failed preflight. Inspect every artifact. Failed sessions are
unscored; never turn them into zero. Save each attempt to a new file. The exporter
regrades code and validates prompts, settings, source hashes, and totals.
Commit source, saved attempts, web data, and downloadable evidence together.
Publish and push only when requested.

Six sessions share 600 seconds of agent time, capped at 120 seconds each.
Select seeds before runs and retain all attempts. Compare matching suite hash,
seed, level, budget, and runtime. One run is not a ranking.

The active API is `/api/v2/results`. Preserve v1.3, v1.2, v1.1, and legacy
source, dependency manifests, exporters, data, artifacts, and APIs. Never use
the legacy merge script on versioned artifacts. See `AGENTS.md` for frozen rules.

## Reproduce or publish the legacy thirteen-task board

`AGENTS.md` contains the board rules. New subject and judge calls use fresh,
read-only headless Codex sessions signed in with the local ChatGPT subscription.
The default judge is `codex-cli/gpt-5.6-sol`; GPT-6 Astra is available as a
subject at `codex-cli/gpt-6-astra`. API and gateway calls require `--allow-api`
and do not belong on this subscription board.

```bash
cd ~/Code/mager-bench
codex login status
.venv/bin/python bench.py --models <codex-cli/model-id> --serial --dry-run
.venv/bin/python -c "from providers import get_provider; print(get_provider('<codex-cli/model-id>').complete('Say OK'))"
.venv/bin/python bench.py --models <codex-cli/model-id> --serial \
  --reasoning-effort low --output runs/YYYY-MM-DD-<model>.json
```

Check that all 13 rows have full responses, the same judge, and no judge errors.
An empty or missing response is a failed call, not a zero score. For long
one-file apps, the CLI judge reads the complete saved answer. The CLI's output
length is prompted, not API-enforced; disclose that alongside scores.

```bash
node web/scripts/merge-subscription-run.mjs runs/YYYY-MM-DD-<model>.json
node web/scripts/sync-results.mjs
cd web && vercel --prod
git add -A && git commit && git push
```

Never write a run directly to `results.json`, mix judges on the same board,
or publish synthetic scores. The Sonnet 5 API board remains an archive.
