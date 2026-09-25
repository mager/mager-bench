---
description: Run a subscription-backed mager-bench eval and publish it
---

# /bench — run and publish a model

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
