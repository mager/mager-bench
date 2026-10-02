# mager-bench web

The model lineup, challenge comparisons, and complete benchmark records at [bench.mager.co](https://bench.mager.co).

| Route | Content |
|---|---|
| `/` | Model lineup, both scoring histories, and a filterable challenge comparison |
| `/challenges` | All thirteen original challenges plus Counterexample, with both scoring methods |
| `/challenges/counterexample-ledger` | Complete Counterexample explanation, interactive example, contract, and methodology |
| `/runs` and `/runs/<id>` | All saved 1.1 attempts, traces, exact coverage, source artifacts |
| `/api/v1.1/results` | Current mutation coverage and full saved responses |
| `/archive` | Historical scoring methods and preserved prompts |
| `/archive/subscription` | Original thirteen-task board, GPT-5.6 Sol judge |
| `/archive/sonnet-5` | Earlier API board with its original judge |
| `/models/<id>` | Unified model profile, original box score, all Counterexample attempts |
| `/models/<id>/<challenge>` | Preserved original submission and judge notes |
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
preliminary evidence, not a definitive model ranking. Models appear together
on the lineup, but the old average and new fault counts are never combined.
Keep version 1.1 artifacts out of `results.json` and the legacy merge script.

The October 1 extension adds three subjects and retains Luna's schema failure
alongside its separate retry. The lineup is the union of legacy and 1.1 models;
missing legacy results are labeled "not run" and have no numeric score. The
supplementary subscription catalogue delegates to the frozen runner. See
`../runs/v1.1/2026-10-01-calibration.md` for the complete record.

## Historical data

`data/results.json` and `data/challenges.json` remain exports of the original
thirteen-task board. `data/sonnet-5-board.json` preserves the older judge.
Only use `merge-subscription-run.mjs` and `sync-results.mjs` for intentional
legacy reproduction. See the canonical `.opencode/commands/bench.md` workflow.

## Development and publication

Read `../PRODUCT.md` and `../DESIGN.md` for the pickup-court design.

```bash
npm run dev
npm run lint
npm run build
vercel --prod
```

Commit source artifacts, exported data, and presentation changes together.
