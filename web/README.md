# mager-bench (web)

The live ChatGPT-subscription scorecard for [mager-bench](../README.md), deployed at [bench.mager.co](https://bench.mager.co).

## Routes

| Path | What |
|---|---|
| `/` | current Codex CLI leaderboard |
| `/models/<id>` | each model's challenge scores |
| `/challenges` | all 13 challenge cards |
| `/challenges/<name>` | prompt, rubric, and current-board scores |
| `/archive/sonnet-5` | earlier API-model board, judged by Sonnet 5 |
| `/experiments/codex-cli-sol` | original GPT-5.6 Sol run with full answers and judge notes |
| `/fund` | notice that the former API funding drive is archived |
| `/api/results` | current board as JSON |

## Data flow

1. `bench.py` saves each subscription-backed model run under `../runs/`.
2. `node scripts/merge-subscription-run.mjs <run-file>` verifies all 13 rows and merges them into `../results.json` without mixing judges.
3. `node scripts/sync-results.mjs` exports the current board to `data/results.json`. Pages and `app/api/results/route.ts` read that file.
4. `data/sonnet-5-board.json` preserves the previous Sonnet board, with its original source in `../runs/2026-09-25-sonnet-5-board-archive.json`.
5. `data/challenges.json` exports prompts and rubrics from `../challenges.py`.
6. `node scripts/sync-cli-result.mjs` exports the original Sol run to `data/codex-cli-sol.json` for its dedicated inspection page.

The old `data/funding.json` remains as an API-era archive. New runs use the local ChatGPT subscription.

## Design and development

See [`../DESIGN.md`](../DESIGN.md) and [`../PRODUCT.md`](../PRODUCT.md) for the CRT design system and product brief.

```bash
npm install
npm run dev
npm run lint
npm run build
vercel --prod
```
