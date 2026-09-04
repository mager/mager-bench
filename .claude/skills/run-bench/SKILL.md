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
- A single `AI_GATEWAY_API_KEY` (Vercel AI Gateway) routes **any** family whose own key is missing, with creator-prefixed ids (`zai/glm-5.3`, `anthropic/claude-sonnet-5`, …) — one key can run subject and judge.
- Smoke-test a new provider/key with a one-line `provider.complete("Say OK")` before burning a full run.

Then merge + publish:

```bash
# merge new rows into results.json (keep other models, refresh generated_at)
node web/scripts/sync-results.mjs      # run from repo root or web/ — reshapes for the dashboard
cd web && vercel --prod                # deploy
git add -A && git commit && git push   # results.json + runs/ are the paper trail — always commit them
```

`sync-results.mjs` also flips `web/data/funding.json` wishlist entries to "scored" automatically when a model appears — no manual edit.

## Known failure modes

| Symptom in the run log | What it actually is | Fix |
|---|---|---|
| `judge error … empty response (finish_reason=length)` + a `0.0` row | The judge's thinking consumed its whole `max_tokens` before emitting the JSON verdict — a **crash, not a score**. Seen with gateway-routed Claude Sonnet 5 on long (debug) responses | Re-run that challenge; `judge.py` ships a 16k judge cap for exactly this |
| Subject `ERROR: … empty response (finish_reason=length)` | A reasoning model (GLM 5.3, gpt-oss) burned its **entire** budget on thinking and shipped zero visible tokens — starvation artifact, never a score | Raise that provider's `THINKING_HEADROOM` (Gateway/Zai ship 32k) and re-run the challenge |
| `finish_reason=length` **with** content | Ordinary truncation at the challenge budget — a real, scoreable result | Score as-is; the cap is part of the challenge |
| `Authentication failed … has access to AI Gateway` (401) | Gateway credential rejected — wrong key type, revoked, project-scoped, or mangled paste | Create a key on the AI Gateway API-keys page (no project scope, team with the credits); `vck_…` prefix |

## Verify before publishing

Scan the run for `judge error` in notes, `0.0` totals, and `ERROR:` lines — those are crashes, not scores (see the table above). Re-run the affected challenges before merging. A model whose challenge genuinely cannot be completed is recorded as **failed for that challenge** — never invent a number for it.

## Common mistakes

| Mistake | Reality |
|---|---|
| Different judge for the new model | Board scores stop being comparable — re-use the existing judge |
| `--output results.json` directly | Wipes every other model's rows |
| Publishing rows with 0.0 judge-error scores | Those are crashes, not scores — re-run first |
| Merging rows from a run that logged `ERROR:` for that challenge | The call produced nothing — starvation or judge crash; re-run or record as failed |
| Forgetting sync + deploy | Board on Vercel stays stale even though results.json updated |
