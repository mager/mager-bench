# Fund the bench

mager-bench is designed to run **without a credit card**.

| Tier | Models | How you run them |
|------|--------|------------------|
| **free** | Llama 3.3 70B, Llama 3.1 8B (Groq), Gemini Flash | free API quotas |
| **cheap** | Claude Haiku 4.5, GPT-4o mini | pennies per full suite |
| **paid** | Sonnet, Opus, GPT-4o, Gemini Pro | crowdfunded or BYO key |

## Why crowdfund?

Paid model evals are the interesting head-to-heads — and they cost real money when you re-run 12 challenges × multi-run averages × multi-judge panels. Free tiers cover the always-on leaderboard; crowdfunding unlocks the expensive seats.

**Where the money goes:** API tokens for published evals only. Every funded run ships raw responses + scores in `results.json`. No ads, no merch.

## How to give

- [Buy Me a Coffee](https://www.buymeacoffee.com/mager)
- GitHub Sponsors — coming soon
- Live drive + wishlist: [mager-bench-web.vercel.app/fund](https://mager-bench-web.vercel.app/fund)

## Tiers

| Name | Amount | What it does |
|------|--------|--------------|
| one coffee | $5 | sponsors roll |
| eval sprint | $25 | fund one full 12-challenge paid-model run |
| season pass | $100 | a month of new-model drops + challenge vote |

## Run free yourself

```bash
export GROQ_API_KEY=...
export GEMINI_API_KEY=...
python bench.py --tier free --judge gemini-2.0-flash --runs 3 --output results.json
cd web && node scripts/sync-results.mjs
```

No Anthropic key required for free-tier subjects + Gemini judge.
