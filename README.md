# mager-bench

A personal coding model benchmark. Twelve tasks I actually care about — from FizzBuzz to a Doom-style raycaster in a single HTML file — run against any combination of models, scored by an LLM judge on correctness, code quality, and documentation. When a new model drops, run `python bench.py` and see where it stands.

The idea is [Simon Willison's pelican-on-a-bicycle test](https://simonwillison.net/tags/pelican-riding-a-bicycle/), but for code: you don't need a giant eval suite to have opinions about models — you need something small and consistent that you run yourself, every time.

**Live dashboard:** [mager-bench-web.vercel.app](https://mager-bench-web.vercel.app) — Claude Haiku 4.5 (avg **6.9**/10) currently leads Claude Sonnet 4.6 (**6.6**) across all 12 challenges.
**Fund paid evals:** [mager-bench-web.vercel.app/fund](https://mager-bench-web.vercel.app/fund) · [FUND.md](./FUND.md)
**JSON API:** [`/api/results`](https://mager-bench-web.vercel.app/api/results)

## Free first

Default runs use **free + cheap** models so a full leaderboard doesn't torch your card:

| Tier | Models | Cost |
|------|--------|------|
| free | `llama-3.3-70b`, `llama-3.1-8b` (Groq), `gemini-2.0-flash`, `gemini-2.5-flash` | $0 free quotas |
| cheap | `claude-haiku-4-5`, `gpt-4o-mini` | pennies / suite |
| paid | `claude-sonnet-*`, `claude-opus-4-8`, `gpt-4o`, `gemini-2.5-pro` | crowdfund or BYO |

Judges are providers too. Default judge is a **free** model when a free key is present (Gemini Flash preferred). No Anthropic key required for free-tier runs.

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

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# free path: just GROQ_API_KEY + GEMINI_API_KEY
```

## Usage

```bash
# free + cheap models, free judge (default)
python bench.py

# wallet-safe only
python bench.py --tier free --judge gemini-2.0-flash

# multi-run mean ± stddev (variance is real — measure it)
python bench.py --tier free --runs 3 --output results.json

# multi-judge panel (averages scores — reduces single-model bias)
python bench.py --models llama-3.3-70b,gemini-2.0-flash \
  --judges gemini-2.0-flash,llama-3.3-70b --runs 2

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
GitHub Sponsors  →  https://github.com/sponsors/mager
Buy Me a Coffee  →  https://www.buymeacoffee.com/mager
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
- **These are my tasks.** Fork it and swap in the twelve things *you* keep asking models to do.

## Adding challenges / models

- Challenges: add a `Challenge` to `CHALLENGES` in `challenges.py`.
- Models: add a `ModelInfo` to `MODELS` in `providers.py` (tier + family + api id).

## License

MIT
