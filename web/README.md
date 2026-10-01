# mager-bench web

The public Counterexample Lab and historical boards at [bench.mager.co](https://bench.mager.co).

| Route | Content |
|---|---|
| `/` | Active 1.1 challenge, oracle-backed walkthrough, preliminary calibration |
| `/challenges` | Current contract and methodology |
| `/runs` and `/runs/<id>` | All saved 1.1 attempts, traces, exact coverage, source artifacts |
| `/api/v1.1/results` | Current mutation coverage and full saved responses |
| `/archive` | Historical scoring methods and preserved prompts |
| `/archive/subscription` | Original thirteen-task board, GPT-5.6 Sol judge |
| `/archive/sonnet-5` | Earlier API board with its original judge |
| `/models/<id>` and `/models/<id>/<challenge>` | Preserved subscription scores and responses |
| `/challenges/<legacy-name>` | Historical prompt, rubric, and scores |
| `/api/results` and `/api/summary` | Backward-compatible legacy data, explicitly labeled archived |

## Current data flow

`bench_v1_1.py` saves independent subscription attempts under `runs/v1.1/`.
From the repository root, run:

```bash
.venv/bin/python web/scripts/sync-counterexample-data.py
```

The exporter verifies suite hashes and prompts, rejects mixed settings, and
regrades every completed response before writing `data/counterexample.json`.
Failed calls must have no score. Offline fixtures are excluded. The interactive
examples are hand-authored and their outputs come directly from the same oracle
and faulty implementations. They are never included as model measurements.

The first calibration contains three attempts per model at low effort. It is
preliminary evidence, shown alphabetically, not a definitive model ranking.
Keep version 1.1 artifacts out of `results.json` and the legacy merge script.

## Historical data

`data/results.json` and `data/challenges.json` remain exports of the original
thirteen-task board. `data/sonnet-5-board.json` preserves the older judge.
Only use `merge-subscription-run.mjs` and `sync-results.mjs` for intentional
legacy reproduction. See the canonical `.opencode/commands/bench.md` workflow.

## Development and publication

Read `../PRODUCT.md` and `../DESIGN.md` for the current light workbench design.

```bash
npm run dev
npm run lint
npm run build
vercel --prod
```

Commit source artifacts, exported data, and presentation changes together.
