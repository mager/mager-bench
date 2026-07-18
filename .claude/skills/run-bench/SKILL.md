---
name: run-bench
description: Use when adding a new model to the mager-bench leaderboard, re-running a model's scores, or publishing bench results to the dashboard — "bench <model>", "add <model> to the board", "run the eval".
---

# Run a bench and publish it

## Core rules

1. **Never mock scores.** Every number on the board comes from a real `bench.py` run.
2. **One judge per board.** Check the judge on the existing board first — new runs must use the same judge or scores aren't comparable:
   ```bash
   python3 -c "import json; print(json.load(open('results.json'))['judge'])"
   ```
3. **Merge, don't overwrite.** `bench.py --output results.json` replaces the whole file. Run new models to a temp file, then merge their rows into `results.json`, keeping existing models' rows.

## Workflow

```bash
cd ~/Code/mager-bench
.venv/bin/python bench.py --models <model-id> --judge <board-judge> \
  --output runs/$(date +%F)-<model-id>.json
```

- Model must exist in `MODELS` in `providers.py` (add a `ModelInfo` if not) with its family's API key in `.env`.
- Smoke-test a new provider/key with a one-line `provider.complete("Say OK")` before burning a full run.

Then merge + publish:

```bash
# merge new rows into results.json (keep other models, refresh generated_at)
node web/scripts/sync-results.mjs      # run from repo root or web/ — reshapes for the dashboard
cd web && vercel --prod                # deploy
git add -A && git commit && git push   # results.json + runs/ are the paper trail — always commit them
```

`sync-results.mjs` also flips `web/data/funding.json` wishlist entries to "scored" automatically when a model appears — no manual edit.

## Verify before publishing

Scan the run for `judge error` in notes or 0.0 totals across the board — those are **judge failures, not real scores**. Re-run those challenges before merging. Known cause: Claude 5-era judges think by default and `max_tokens` caps thinking + text; the judge call needs a generous cap (see `judge.py`).

## Common mistakes

| Mistake | Reality |
|---|---|
| Different judge for the new model | Board scores stop being comparable — re-use the existing judge |
| `--output results.json` directly | Wipes every other model's rows |
| Publishing rows with 0.0 judge-error scores | Those are crashes, not scores — re-run first |
| Forgetting sync + deploy | Board on Vercel stays stale even though results.json updated |
