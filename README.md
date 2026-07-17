# mager-bench

A personal coding model benchmark. Twelve tasks I actually care about — from FizzBuzz to a Doom-style raycaster in a single HTML file — run against any combination of models, scored by an LLM judge on correctness, code quality, and documentation. When a new model drops, run `python bench.py` and see where it stands.

The idea is [Simon Willison's pelican-on-a-bicycle test](https://simonwillison.net/tags/pelican-riding-a-bicycle/), but for code: you don't need a giant eval suite to have opinions about models — you need something small and consistent that you run yourself, every time.

**Live dashboard:** [mager-bench-web.vercel.app](https://mager-bench-web.vercel.app) — Claude Haiku 4.5 (avg **6.9**/10) currently leads Claude Sonnet 4.6 (**6.6**) across all 12 challenges. Same data as JSON at [`/api/results`](https://mager-bench-web.vercel.app/api/results).

## Challenges

| Name | What it tests |
|------|--------------|
| `fizzbuzz` | Baseline correctness + code style |
| `binary-search` | Algorithm + full docstring (Args/Returns/Raises + examples) |
| `api-client` | Class design + error handling + type hints + docs |
| `readme-writer` | Pure documentation ability — no code at all |
| `refactor` | Code clarity + whether the model can explain its changes |
| `test-writing` | Pytest tests for a provided function — edge-case thinking + assertion quality |
| `debug` | Find and fix 3 bugs in broken Python — careful reading + correctness reasoning |
| `async-fetch` | Async Python: concurrent HTTP fetching with timeout and retry |
| `sql` | Complex SQL with CTEs, window functions, and aggregations |
| `go-test` | Idiomatic Go table-driven tests — Go testing conventions |
| `elixir-test` | Idiomatic Elixir ExUnit tests — Elixir testing conventions |
| `doom` | A Doom-style raycasting FPS engine in a single HTML file — the signature challenge |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# fill in the API keys for the models you want to test
```

Models run if their key is present, and are skipped if not — an `ANTHROPIC_API_KEY` is always required because the judge is a Claude model.

## Usage

```bash
# run all challenges against all configured models (models run in parallel)
python bench.py

# specific models
python bench.py --models claude-sonnet-5,gpt-4o

# one challenge
python bench.py --challenge binary-search

# score with a different judge (any Anthropic model ID)
python bench.py --judge claude-opus-4-8

# one model at a time — cleaner latency numbers
python bench.py --serial

# save results to JSON (includes judge + timestamp for provenance)
python bench.py --output results.json

# list available models / challenges
python bench.py --list-models
python bench.py --list-challenges
```

Built-in model IDs: `claude-opus-4-8`, `claude-sonnet-5`, `claude-sonnet-4-6`, `claude-haiku-4-5`, `gpt-4o`, `gpt-4o-mini`, `gemini-2.0-flash`, `gemini-2.5-pro`.

## Example output

```
── binary-search ──────────────────────────────────
  claude-sonnet-5: total=9.0  (4213ms)
  gpt-4o: total=7.7  (3187ms)
  claude-haiku-4-5: total=7.3  (2094ms)

═══ RESULTS ═══════════════════════════════════════════════════
Judge: claude-sonnet-5
Model                          Challenge            Correct Quality    Docs    Speed   Total
──────────────────────────────────────────────────────────────────────────────────────────
claude-sonnet-5                binary-search            9.0     9.0     9.0   4213ms     9.0
gpt-4o                         binary-search            8.0     8.0     7.0   3187ms     7.7
...
```

## Scoring

Each response goes to an LLM judge (default: `claude-sonnet-5`) that reads it against the challenge's rubric and scores three dimensions from 0–10:

- **Correctness** — does the code actually solve the problem, including edge cases?
- **Code Quality** — idiomatic, clean, well-structured?
- **Documentation** — docstrings, comments, examples — useful, not boilerplate?

**Total** = average of the three. Speed (ms) is measured separately and shown but doesn't affect the score. The judge uses [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), so scores always come back as schema-valid JSON — no regex parsing of model chatter.

## Web dashboard

`web/` is a small Next.js app (deployed on Vercel) that renders the latest `results.json` as a scorecard/leaderboard, and re-exposes it as JSON at `GET /api/results`.

```bash
# after running bench.py --output results.json at the repo root:
cd web
node scripts/sync-results.mjs   # reshapes ../results.json -> web/data/results.json
npm run dev                     # or: vercel --prod to redeploy
```

The dashboard leaderboard stacks every model in `results.json` — run more models through `bench.py`, re-sync, redeploy, and they show up ranked.

Each challenge also has its own definition page at `/challenges/<name>` — the exact prompt, the rubric per dimension, and how every model that's run it scored. If `challenges.py` changes, re-export `web/data/challenges.json`:

```bash
python3 -c "
import json, dataclasses
from challenges import CHALLENGES
print(json.dumps([dataclasses.asdict(c) for c in CHALLENGES], indent=2))
" > web/data/challenges.json
```

## Caveats (read before quoting numbers)

- **The judge is a model too.** By default Claude scores everyone, including other Claude models. If that bothers you (it should, a little), re-run with `--judge` set to a different model and compare. Rankings have been stable across judges in my runs, but verify for yours.
- **Single-run variance is real.** One run is a vibe check, not a leaderboard. Scores on the same model can move ±1 point between runs.
- **These are my tasks.** That's the point. Fork it and replace the challenges with the things *you* keep asking models to do.

## Adding challenges

Add a new `Challenge` to `CHALLENGES` in `challenges.py` with a `name`, `description`, `prompt`, and a `rubric` dict with `correctness`, `quality`, and `documentation` keys describing what the judge should look for.

## Adding models

Add an entry to `AVAILABLE_MODELS` and `_MODEL_MAP` in `providers.py`, then implement or reuse a `Provider` subclass (Anthropic, OpenAI, and Gemini adapters are included).

## License

MIT
