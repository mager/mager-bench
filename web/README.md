# mager-bench (web)

The live scorecard/leaderboard for [mager-bench](../README.md), deployed at
[mager-bench-web.vercel.app](https://mager-bench-web.vercel.app).

## Data flow

1. `python bench.py --output results.json` at the repo root produces raw per-challenge results.
2. `node scripts/sync-results.mjs` reshapes that into `data/results.json` (grouped by model, with averages).
3. `app/page.tsx` renders it; `app/api/results/route.ts` re-serves the same file as JSON.

## Develop

```bash
npm install
npm run dev
```

## Deploy

```bash
vercel --prod
```
