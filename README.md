# mager-bench

A personal coding model benchmark. Thirteen tasks I actually care about — from FizzBuzz to a Doom-style raycaster in a single HTML file — run against any combination of models, scored by an LLM judge on correctness, code quality, and documentation. When a new model drops, run `python bench.py` and see where it stands.

The idea is [Simon Willison's pelican-on-a-bicycle test](https://simonwillison.net/tags/pelican-riding-a-bicycle/), but for code: you don't need a giant eval suite to have opinions about models — you need something small and consistent that you run yourself, every time.

**Live dashboard:** [bench.mager.co](https://bench.mager.co) — GLM 5.3 debuts at #1 (avg **6.8**/10) ahead of GPT-OSS 120B (**6.4**) across all 13 challenges, all judged by Claude Sonnet 5 — with doom + slots recorded as failed for GLM (see caveats).
**Fund paid evals:** [bench.mager.co/fund](https://bench.mager.co/fund) · [FUND.md](./FUND.md)
**JSON API:** [`/api/results`](https://bench.mager.co/api/results)

## Free first

Default runs use **free + cheap** models so a full leaderboard doesn't torch your card:

| Tier | Models | Cost |
|------|--------|------|
| free | `llama-3.3-70b`, `llama-3.1-8b`, `gpt-oss-120b` (Groq), `gemini-2.5-flash` | $0 free quotas |
<| cheap | `claude-haiku-4-5`, `gpt-4o-mini`, `glm-5.3-promo` (AI Gateway) | pennies / suite |
| paid | `claude-sonnet-*`, `claude-opus-4-8`, `gpt-4o`, `gemini-2.5-pro`, `glm-5.3` | crowdfund or BYO |

Judges are providers too. Default judge is a **free** model when a free key is present (Gemini Flash preferred). No Anthropic key required for free-tier runs. One `AI_GATEWAY_API_KEY` (Vercel AI Gateway) can serve any model — subject or judge — when a family's own key is missing. Spend shows up under AI Gateway Logs/Usage. Cap the burn: `--thinking-budget 2048`, `--reasoning-effort low`, and `--dry-run` first on anything paid.

## Challenges

| Name | What it tests |
|------|--------------|
| `fizzbuzz` | Baseline correctness + code style |
| `binary-search` | Algorithm + full docstring (Args/Returns/Raises + examples) |
| `api-client` | Class design + error handling + type hints + docs |
| `readme-writer` | Pure documentation ability — no code at all |
| `refactor` | Code clarity + whether the model can explain its changes |
| `test-writing` | Edge-case thinking + pytest parametrize discipline |
| `debug` | Careful reading + correctness reasoning over broken code |
| `async-fetch` | Async concurrency patterns + retry/timeout handling |
| `sql` | CTE + window function fluency on a real schema |
| `go-test` | Idiomatic Go table-driven tests + benchmark |
| `elixir-test` | ExUnit describe blocks + assert_raise + unicode handling |
| `doom` | DDA raycaster FPS — the signature hard challenge |
<| `slots` | Vegas slot machine in a single HTML file — reels, pay table, betting, win animations |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# free path: just GROQ_API_KEY + GEMINI_API_KEY
# one-key-everything: AI_GATEWAY_API_KEY (Vercel AI Gateway)
```

## Usage (opencode first)

`/bench` in opencode is the primary harness — dry-run, caps, merge, and
publish flow. See `AGENTS.md`. Raw CLI for everything else:

```bash
# free + cheap models, free judge (default)
python bench.py

# wallet-safe only
python bench.py --tier free --judge gemini-2.5-flash

# dry-run before spending (models × challenges × runs, no API calls)
python bench.py --models glm-5.3 --runs 3 --dry-run

# gateway run with caps on (tames thinking-token burn)
python bench.py --models glm-5.3 --reasoning-effort low --thinking-budget 2048

# multi-run mean ± stddev (variance is real — measure it)
python bench.py --tier free --runs 3 --output results.json

# multi-judge panel (averages scores — reduces single-model bias)
python bench.py --models llama-3.3-70b,gemini-2.5-flash \
  --judges gemini-2.5-flash,llama-3.3-70b --runs 2

# one challenge / serial latency
python bench.py --challenge doom --serial

# list models (shows tier + whether the key is present)
python bench.py --list-models
python bench.py --list-challenges
```

## Scoring

Each response is scored 0–10 on three dimensions:

- **Correctness** — does the code actually solve the problem, including edge cases?
- **Code Quality** — idiomatic, clean, well-structured?
- **Documentation** — docstrings, comments, examples — useful, not boilerplate?

**Total** = average of the three. Speed (ms) is shown but not scored.

With `--runs N`, totals are means and the table shows ±σ. With `--judges a,b`, numeric scores are averaged across the panel.

## Crowdfunding

Paid models (Opus, GPT-4o, …) stay on a public wishlist until funded. See **[FUND.md](./FUND.md)** and the live `/fund` page. Dollars only buy API tokens for published evals — every funded run ships raw responses in `results.json`.

```
Buy Me a Coffee  →  https://www.buymeacoffee.com/mager
GitHub Sponsors  →  coming soon
```

## Web dashboard

`web/` is a Next.js CRT amber dashboard (Vercel) with multi-model leaderboard, per-challenge pages, fund drive, and `GET /api/results`.

```bash
python bench.py --tier free --runs 3 --output results.json
cd web
node scripts/sync-results.mjs   # reshapes ../results.json → web/data/results.json
npm run dev
```

The dashboard leaderboard stacks every model in `results.json` — run more models through `bench.py`, re-sync, redeploy, and they show up ranked.

Each challenge also has its own definition page at `/challenges/<name>` — the exact prompt, the rubric per dimension, and how every model that's run it scored. Re-export challenge definitions after editing `challenges.py`:

```bash
python3 -c "
import json, dataclasses
from challenges import CHALLENGES
print(json.dumps([dataclasses.asdict(c) for c in CHALLENGES], indent=2))
" > web/data/challenges.json
```

## Caveats

- **The judge is a model too.** Prefer multi-judge panels (`--judges`) and free judges so Claude isn't grading Claude alone.
- **Single-run variance is real.** Use `--runs 3` before quoting numbers.
- **A failed challenge is a real result.** GLM 5.3's doom and slots rows are recorded as 0.0 — its reasoning consumed the entire token budget before producing any visible output, on both the standard budget and a 4× thinking-headroom retry. Nothing was judged because there was nothing to score; no number was invented to fill the gap.
- **These are my tasks.** Fork it and swap in the thirteen things *you* keep asking models to do.

## Adding challenges / models

- Challenges: add a `Challenge` to `CHALLENGES` in `challenges.py`.
- Models: add a `ModelInfo` to `MODELS` in `providers.py` (tier + family + api id — families without their own key route through the Vercel AI Gateway with a `creator/` prefix).

## License

MIT
