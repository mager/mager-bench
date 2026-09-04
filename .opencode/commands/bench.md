---
description: Run a mager-bench eval and publish it to the leaderboard
---

# /bench — run a bench and publish it

Primary harness for mager-bench. Full wallet + board rules live in `AGENTS.md`
at the repo root — follow them.

## Workflow

```bash
cd ~/Code/mager-bench
```

1. **Check the board judge** — new runs must reuse it or scores aren't comparable:
   ```bash
   .venv/bin/python -c "import json; print(json.load(open('results.json'))['judge'])"
   ```
2. **Dry-run first** (mandatory for paid/gateway models):
   ```bash
   .venv/bin/python bench.py --models <model-id> --judge <board-judge> --runs <n> --dry-run
   ```
3. **Smoke-test the key** with a one-line `complete("Say OK")` before a full run.
4. **Run wallet-safe** — add caps on paid/gateway runs:
   ```bash
   .venv/bin/python bench.py --models <model-id> --judge <board-judge> --runs <n> \
     --thinking-budget 2048 --reasoning-effort low \
     --output runs/$(date +%F)-<model-id>.json
   ```
   Big builds (doom/slots via thinking models): add `--thinking-headroom 32768`.
   Sonnet judge on long responses: `--judge-max-tokens 16384`. Both are billed
   only on use; without them you get starvation empties, not scores.
   Model must exist in `MODELS` in `providers.py` (add a `ModelInfo` if not)
   with its family's key in `.env` (`AI_GATEWAY_API_KEY` for `gateway` models).
5. **Verify** — scan for `judge error` notes or 0.0 totals: those are judge
   crashes, not scores. Re-run those challenges before merging.
6. **Merge + publish** (never `--output results.json` — it wipes the board):
   ```bash
   node web/scripts/sync-results.mjs
   cd web && vercel --prod
   git add -A && git commit && git push
   ```

Judge guidance: free judge (Gemini Flash) for bulk runs, Sonnet judge only for
final validation. `glm-5.3-promo` for cheap reruns (prompt-cached).
