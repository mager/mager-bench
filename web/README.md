# mager-bench (web)

The live scorecard/leaderboard for [mager-bench](../README.md), deployed at
[bench.mager.co](https://bench.mager.co).

## Routes

| Path | What |
|------|------|
| `/` | multi-model leaderboard + per-model challenge breakdowns + fund teaser |
| `/challenges` | all 13 challenge cards |
| `/challenges/<name>` | prompt, rubric, per-model scores |
| `/fund` | crowdfunding drive, tiers, paid-model wishlist |
| `/experiments/codex-cli-sol` | separate GPT-5.6 Sol headless Codex run with full responses and judge notes |
| `/api/results` | same JSON as the dashboard |

## Data flow

1. `python bench.py --tier free --runs 3 --output results.json` at the repo root.
2. `node scripts/sync-results.mjs` reshapes that into `data/results.json` (grouped by model, with averages + tier tags) and merges wishlist status from `data/funding.json`.
3. Pages render it; `app/api/results/route.ts` re-serves the same file as JSON.
4. `data/challenges.json` is an export of prompts/rubrics from `../challenges.py` — re-export if challenges change.
5. `data/funding.json` is the crowdfunding config (goal, tiers, wishlist, sponsor links). Edit it when the season goal or wishlist changes.
6. `node scripts/sync-cli-result.mjs` validates and exports the separate Codex CLI run to `data/codex-cli-sol.json`. Its self-judged scores never enter the Sonnet leaderboard.

## Design system

See [`../DESIGN.md`](../DESIGN.md) for the color/typography tokens (CRT amber
theme + green/magenta/cyan per-dimension accents) and [`../PRODUCT.md`](../PRODUCT.md)
for the register/brand brief. Crowdfunding voice lives in [`../FUND.md`](../FUND.md).

## Develop

```bash
npm install
npm run dev
```

## Deploy

```bash
vercel --prod
```
