# mager-bench 2.0

Three small JavaScript repositories. Fix a defect, then implement a change.
The code on disk is the submission. Codex can inspect files, edit code, add
local tests, and run commands. Use the local ChatGPT subscription only.

## Tasks and scoring

| Project | First work order | Second work order |
| --- | --- | --- |
| Event ledger | Duplicate events and insufficient funds | Atomic batches and account versions |
| Incremental build | Dependency order and cache invalidation | Dependency changes, cycles, and cache rollback |
| Access policy | Tenant isolation and deny precedence | Role inheritance, cycle rejection, and expiry |

Each work order has 32 deterministic checks. The first order has eight fixed
boundary cases and 24 generated cases. The second has eight boundary cases,
eight regression cases, and 16 generated cases. A case passes only when its
entire output matches. Object key order is ignored; array order and value types
matter. Each case earns one point, for 192 total. A project passes only if both
orders pass all 64 checks. Report correctness, elapsed time, and token use
separately. There is no combined ranking score and no model judge.

Expected outputs come from independent Python oracles. Author-written JavaScript
reference implementations cross-check the oracles. Mutation tests verify that
known defects fail. Reference code is a fixture, never a model result.
Exact contracts are in `agent_bench_v2/tasks.py`; cases and oracles are beside it.

## Execution

Six fresh `codex exec` sessions run in series. Each project keeps its files
between orders, but conversation history is reset. The second prompt repeats
the first contract and adds the change. Evaluation results are not given to
the agent between orders. The visible repository includes two smoke tests.

The six sessions share 600 seconds of agent time, capped at 120 seconds per
session. This time includes CLI startup, generation, and local tool use. Local
grading and the login check are outside that limit. A separate, unscored
file-edit probe is capped at 30 seconds. It verifies account access and tools.

Always use the lowest supported reasoning effort. The runner selects it from
the local Codex catalog and saves the supported levels and selected value.
Catalog presence does not prove account access. The CLI must report a ChatGPT
login. The runner removes API-key and gateway environment variables, ignores
user config and rules, selects the built-in OpenAI provider, and forces ChatGPT
authentication. There is no API fallback or model substitution.

The runner never retries a session. Codex can retry transport requests internally;
its built-in provider does not accept per-provider retry overrides in CLI 0.154.0.
Saved events and the CLI version make that limit visible. Any emitted error or
failed-turn event, nonzero exit, timeout, or missing final response stops the run.
A failed run has no overall score. Earlier completed phases remain visible as
partial evidence. Wrong code fails checks; it is not a provider failure.

Workspace writes are sandboxed. Agent network tools and web search are disabled.
Agents can run Node tests. Evaluation code is snapshotted and run separately in
QuickJS, with no host bindings. Each case has 32 MiB memory, a 1 MiB stack, and
500 ms CPU time. Source is limited to 24 relative CommonJS `.js` files under
`src/`, totaling 128 KiB. Input mutation is rejected. Symlinks, invalid sources,
and changes to protected starter files fail the phase's checks.

## Seeds, scale, and comparisons

A seed fixes all generated inputs. Select seeds before running models; keep all
attempts. Level 1 uses base sizes of 8 entities and 24 operations; level 2 uses
32 and 96; level 3 uses 128 and 384. Build cases use `max(8, operations // 4)`
requests. Policy cases add sentinel records to detect constant-deny solutions.
Boundary cases have their own fixed sizes, including an 80-node shared DAG.
All levels still have 192 checks. Level is workload size, not a calibrated
measure of difficulty.

Compare only the same suite hash, seed, level, runtime, and budget. Compare
models across several preselected seeds and report per-task failures and run
variation. A single run is a smoke calibration, not a leaderboard. Host speed,
CLI version, subscription routing, service load, and prompt caching affect time.
Saved usage is the CLI's reported usage; it is not a dollar cost estimate.

## Evidence

Each artifact records model and effort, seed and level, suite fingerprint,
runtime versions, prompts, CLI events, responses, usage, timing, source snapshots,
diffs, and exact input/expected/actual results for every check. Failed attempts
remain unscored. A setup failure can have no code or model events.

`--replay` reruns the saved source locally, without any model calls. The exporter
also regrades completed phases and verifies prompts, settings, source hashes,
completion events, and totals. It exports exact raw evidence for download plus
a smaller site index. Logs are local evidence, not cryptographic proof of model
identity. The evaluator does not claim to detect fabricated logs.

The initial preflight failed before a model call because CLI 0.154.0 rejected
retry overrides for the built-in provider. That artifact is retained under its
original source hash. Failed preflight artifacts may have an older suite hash;
they can never become scored results. Scored evaluations must match the current
suite hash exactly.

## Run

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
.venv/bin/python bench_v2.py --replay runs/v2/YYYY-MM-DD-<model>-seed42-level1-r1.json
.venv/bin/python web/scripts/sync-agent-v2-data.py
.venv/bin/python -m unittest discover -s tests
npm --prefix web run lint
npm --prefix web run build
```

Stop after a failed preflight. Diagnose it and retain its evidence; do not silently
retry or replace the model. Run outputs must use a new file directly in `runs/v2/`.
Commit source, artifacts, `web/data/agent-v2.json`, and downloadable evidence in
`web/public/evidence/v2/` together. Never merge v2 into `results.json`.

## Scope and future versions

This is a test of repairs and changing requirements in small synthetic projects.
It does not measure large application design, user interfaces, deployment,
external integrations, or long-term conversational memory. Public generators
are not secret tests. Test inputs are outside the agent workspace, but the local
CLI sandbox does not fully isolate host reads. This is not a secure adversarial
benchmark or a contamination-proof evaluation.

The extensible parts are separate task contracts, generators, oracles, snapshots,
and replay. Future versions can add projects and capabilities. No fixed suite
can be guaranteed to stay hard for five or ten years. Freeze this version once
published. A change to contracts, corpus/generator, budget, or scoring requires
a new version. Keep old scores and artifacts separate. Versions 1.3, 1.2, 1.1,
and the original thirteen-task board remain frozen and accessible in the archive.

## First calibration

On October 24, 2026, GPT-6 Astra at low effort passed 192/192 checks on seed 42,
level 1. It used 235.134 seconds of agent time. All three projects passed both
orders. Replay reproduced the result. This is one calibration run; level 1 did
not distinguish performance within that run. It does not establish a ranking
or demonstrate that the higher workloads are difficult for frontier models.
