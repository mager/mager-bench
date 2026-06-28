# mager-bench

A coding model benchmark that rates AI models on correctness, code quality, documentation, and speed.

Uses LLM-as-judge (Claude Sonnet) to score responses across 5 challenges. Models compete head-to-head on the same prompts.

## Challenges

| Name | What it tests |
|------|--------------|
| `fizzbuzz` | Basic correctness + code style |
| `binary-search` | Algorithm + full docstring |
| `api-client` | Class design + error handling + docs |
| `readme-writer` | Documentation ability directly |
| `refactor` | Code clarity + explanation quality |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# fill in the API keys for models you want to test
```

## Usage

```bash
# run all challenges against all configured models
python bench.py

# specific models
python bench.py --models claude-opus-4-8,gpt-4o

# one challenge
python bench.py --challenge binary-search

# save results to JSON
python bench.py --output results.json

# list available models / challenges
python bench.py --list-models
python bench.py --list-challenges
```

## Scoring

Each response is scored 0–10 on three dimensions by Claude Sonnet:

- **Correctness** — does the code actually solve the problem?
- **Code Quality** — idiomatic, clean, well-structured?
- **Documentation** — docstrings, comments, examples?

**Total** = average of the three. Speed (ms) is measured separately and shown but doesn't affect the score.

## Adding challenges

Add a new `Challenge` to `CHALLENGES` in `challenges.py` with a `name`, `description`, `prompt`, and a `rubric` dict with `correctness`, `quality`, and `documentation` keys describing what to look for.

## Adding models

Add a new entry to `_MODEL_MAP` and `_KEY_MAP` in `providers.py`, then implement or reuse a `Provider` subclass.
