---
description: Run mager-bench 1.1 through the local ChatGPT subscription
---

# /bench — run mager-bench 1.1

The active suite is Counterexample Lab. Read `docs/mager-bench-1.1.md` and
`counterexample_lab/prompt.md`. The model supplies regression traces; a
deterministic grader measures how many of eight ledger faults they expose.
There are no LLM judge calls. Use the local ChatGPT subscription exclusively.

```bash
cd ~/Code/mager-bench
codex login status
.venv/bin/python bench_v1_1.py --model <codex-cli/model-id> --dry-run
.venv/bin/python -c "from providers import get_provider; print(get_provider('<codex-cli/model-id>').complete('Say OK'))"
.venv/bin/python bench_v1_1.py --model <codex-cli/model-id> \
  --reasoning-effort low --output runs/v1.1/YYYY-MM-DD-<model>-r1.json
```

Save each independent attempt with a new filename. Inspect status, raw response,
suite hash, reasoning effort, trace validity, and exposed faults. An empty or
malformed response or provider error is an unscored failed call, never a zero.
Preserve failed attempts when rerunning. Calibration requires repeated samples
with matching effort, output targets, and suite hashes. The first six attempts
are published as preliminary calibration, without ranking the models.

Commit new run artifacts with their frozen test source and generated web data.
Never run the legacy merge script on 1.1 artifacts. To publish compatible runs:

```bash
.venv/bin/python web/scripts/sync-counterexample-data.py
cd web
npm run lint
npm run build
vercel --prod
```

The exporter regrades each completed response and rejects mismatched suite
hashes, prompts, or settings. Commit and push the source artifacts, exported
`web/data/counterexample.json`, and any presentation changes together.
The homepage and `/api/v1.1/results` use the new data. `results.json`,
`/api/results`, and `/api/summary` retain the legacy scoring contract; the old
subscription board lives at `/archive/subscription`. FizzBuzz, binary search,
and refactor are retired from the active suite; historical evidence stays intact.

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
