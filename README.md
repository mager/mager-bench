# mager-bench

Can a coding agent fix a bug, then handle a change?

Version 2 uses three small JavaScript projects: an event ledger, a build cache,
and an access policy engine. Six work orders. 192 checks. Ten minutes of agent
time. Codex CLI with a ChatGPT subscription, at the lowest supported effort.
No model judge.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-v2.txt
codex login status
.venv/bin/python bench_v2.py --self-test --level 3
.venv/bin/python bench_v2.py --model codex-cli/<model> --smoke --dry-run
.venv/bin/python bench_v2.py --model codex-cli/<model> --smoke \
  --output runs/v2/YYYY-MM-DD-<model>-preflight.json
.venv/bin/python bench_v2.py --model codex-cli/<model> --seed 42 --level 1 --dry-run
.venv/bin/python bench_v2.py --model codex-cli/<model> --seed 42 --level 1 \
  --output runs/v2/YYYY-MM-DD-<model>-seed42-level1-r1.json
```

Stop if the CLI check fails. Every attempt is saved. Failed sessions are unscored.
The runner does not retry or substitute models. CLI network retries can occur.

- [Rules, limits, and reproduction](docs/mager-bench-2.0.md)
- [Task contracts](agent_bench_v2/tasks.py)
- [Saved attempts](runs/v2/)
- [Agent workflow](.opencode/commands/bench.md)
- [Website](https://bench.mager.co/)

Run `.venv/bin/python -m unittest discover -s tests` to check the harness.
Use `bench_v2.py --replay <artifact>` to regrade saved code without model calls.
Export with `.venv/bin/python web/scripts/sync-agent-v2-data.py`.

These are public synthetic projects. One run is not a ranking. Match suite hash,
seed, level, budget, and runtime when comparing results. New capabilities belong
in new versions. Versions 1.3, 1.2, 1.1, and the original thirteen-task suite are
frozen in the [archive](https://bench.mager.co/archive).

## Checks

```sh
.venv/bin/python -m pip install -r requirements-dev-v2.txt
npm ci --prefix web
./scripts/check-v2.sh
npm --prefix web run build
```

The check command runs Ruff, all harness tests, a read-only evidence replay and
export check, ESLint, and TypeScript. It makes no model calls. CI runs the same
checks and the production build on pushes and pull requests. The legacy-provider
tests mock the API SDK; no API key is required. `ruff.toml` records the reviewed
exceptions for deterministic RNG, equal-length list comparison, and CLI calls.
Scored source files and saved evidence remain unchanged.
