# mager-bench (web)

The live scorecard/leaderboard for [mager-bench](../README.md), deployed at
[mager-bench-web.vercel.app](https://mager-bench-web.vercel.app).

## Data flow

1. `python bench.py --output results.json` at the repo root produces raw per-challenge results.
2. `node scripts/sync-results.mjs` reshapes that into `data/results.json` (grouped by model, with averages).
3. `app/page.tsx` renders it; `app/api/results/route.ts` re-serves the same file as JSON.
4. `data/challenges.json` is a one-time export of the real prompts/rubrics from `../challenges.py`
   (via `python -c "..."`, see repo root README) — powers `app/challenges/` (index + one definition
   page per challenge, at `/challenges/<name>`). Re-export it if `challenges.py` changes.

## Design system

See [`../DESIGN.md`](../DESIGN.md) for the color/typography tokens (CRT amber
theme + green/magenta/cyan per-dimension accents) and [`../PRODUCT.md`](../PRODUCT.md)
for the register/brand brief.

## Develop

```bash
npm install
npm run dev
```

## Deploy

```bash
vercel --prod
```
