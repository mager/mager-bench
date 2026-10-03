---
description: Run the fast mager-bench 1.3 suite through the local ChatGPT subscription
---

# /bench — mager-bench 1.3

Read `docs/mager-bench-1.3.md`. Two algorithmic and three everyday programs, 60 exact checks,
zero model judges. Always use the lowest supported reasoning effort. The runner
selects it automatically from the local Codex catalog and records the choice.
No higher-effort override, retries, substitute models, or API fallback.

```sh
codex login status
.venv/bin/python bench_v1_3.py --model codex-cli/<model-id> --dry-run
.venv/bin/python bench_v1_3.py --model codex-cli/<model-id> \
  --output runs/v1.3/YYYY-MM-DD-<model>-r1.json
.venv/bin/python web/scripts/sync-everyday-v1.3-data.py
.venv/bin/python -m unittest discover -s tests
npm --prefix web run lint
npm --prefix web run build
cd web
vercel --prod --yes
```

Inspect every artifact before publishing. Provider failures and empty outputs
are unscored; never turn them into zero. The exporter regrades successful code
and checks prompts, settings, and source fingerprints. Commit source, saved
runs, and generated `web/data/everyday-v1.3.json` together, then push.

GPT-6 Sol was rejected by the subscription CLI on October 2, 2026. Its failed
first v1.2 attempt is preserved under `runs/v1.2/`. Do not silently replace it.

Five calls share at most 270 seconds of provider waiting, with a 90-second cap
per call. No v1.3 model attempts are published yet. Version 1.2 is frozen at
`/archive/v1.2`; preserve its source, exporter, web data and artifacts.

The active data API is `/api/v1.3/results`. Counterexample Lab is frozen at
`/archive/v1.1`; its original runner, hashes, artifacts, and APIs remain intact.
The original thirteen-task subscription board is at `/archive/subscription`.
Never run the legacy merge script on v1.1, v1.2, or v1.3 artifacts.

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
