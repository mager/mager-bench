---
name: add-challenge
description: Use when adding, editing, or removing a benchmark challenge in mager-bench — "add a challenge", "new task for the bench", changes to challenges.py or the /challenges pages.
---

# Add or edit a challenge

## Workflow

1. **Define it** — add a `Challenge` to `CHALLENGES` in `challenges.py`: name (kebab-case), description, prompt, and a rubric with all three keys (`correctness`, `quality`, `documentation`).

2. **Re-export definitions for the web** (the `/challenges/<name>` pages read a static JSON, not challenges.py):
   ```bash
   cd ~/Code/mager-bench && python3 -c "
   import json, dataclasses
   from challenges import CHALLENGES
   print(json.dumps([dataclasses.asdict(c) for c in CHALLENGES], indent=2))
   " > web/data/challenges.json
   ```

3. **Add a one-liner to `DESCRIPTIONS`** in `web/scripts/sync-results.mjs` — unknown challenges render with an empty description on the leaderboard.

4. **Backfill scores** — existing models have no rows for the new challenge until re-run:
   ```bash
   .venv/bin/python bench.py --models <each-model-on-board> --challenge <name> \
     --judge <board-judge> --output runs/$(date +%F)-<name>-backfill.json
   ```
   Use the board's existing judge (see the run-bench skill) and merge rows into `results.json` — never overwrite it.

5. **Sync + deploy + commit** — `node web/scripts/sync-results.mjs`, `cd web && vercel --prod`, commit `challenges.py`, `web/data/challenges.json`, `results.json`, `runs/`.

## Common mistakes

| Mistake | Reality |
|---|---|
| Editing challenges.py only | `/challenges` pages read `web/data/challenges.json` — stale until re-exported |
| Skipping the backfill | New challenge shows for some models and not others; averages skew |
| New rubric missing a dimension key | `judge.py` formats all three rubric keys — KeyError at judge time |
