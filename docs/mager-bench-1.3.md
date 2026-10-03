# mager-bench 1.3

Five JavaScript tasks, 60 deterministic checks, lowest supported reasoning
effort. This release adds two algorithmic tasks to the three practical programs
from 1.2. Low effort is a constraint on the model, not a reason to make the
questions easy. Actual model difficulty has not yet been calibrated.

## New algorithmic tasks

**Plan a dependency build.** Compute only the jobs required by the requested
targets. Detect cycles in that subgraph, produce the smallest valid topological
order, and find the minimum parallel completion time and canonical critical
path. Shared dependencies, unrelated cycles, duplicate edges, zero durations,
and ties all have explicit semantics. One 80-job graph has 40 layers and over
one trillion root-to-target paths across its two targets. A memoized graph
algorithm handles it without enumerating those paths.

**Choose the best jobs.** Find an exact maximum-profit, non-overlapping schedule
under a spending budget and cooldown constraint. Resolve ties by cost, job
count, then chronological ID sequence. Greedy profit, earliest-finish, and
profit-per-cost choices can fail. One case has 80 jobs and a budget of 40;
exhaustive subset enumeration is impractical, while dynamic programming fits
comfortably within the local execution limit.

Each new task has twelve public cases. Weighted bill settlement, contact CSV
cleanup, and meeting-time search retain their exact twelve cases and prompts
from version 1.2. Task order is graph, optimization, bill, CSV, meeting.
Contracts, input bounds, and literal expected results are in
`everyday_v1_3/tasks.py`. All tasks ask for a synchronous `solve(input)` function.

## Keep the benchmark fast

The runner automatically selects the lowest effort in the local Codex catalog.
There is no higher-effort override. Each task gets one answer, a 3,072-token
prompted output target, and at most 90 seconds of provider waiting. Five calls
share a **270-second total generation waiting budget**, the same maximum waiting
time as the three-call 1.2 suite. Later calls receive the remaining allowance.
This is not a 270-second end-to-end wall-clock guarantee: login, file writes,
and local grading add overhead. No retries, model substitutions, API calls,
gateways, or LLM judges. The first provider/format failure stops the run.

Each case runs in a fresh QuickJS context with 16 MiB memory, a 256 KiB stack,
and 100 ms CPU time. No host filesystem, process, network or Python bindings
are exposed. Standard synchronous JavaScript only. See the inherited
[v1.2 protocol](mager-bench-1.2.md) for the interpreter's security limitations.

Each check is one point for an exact JSON result. Arrays are ordered; object
key order is ignored; booleans and numbers are distinct. Wrong code, code
exceptions, memory exhaustion, and interpreter timeouts fail checks. Missing,
empty or oversized answers, provider failures, interruptions, and an exhausted
generation budget leave the overall attempt unscored. Completed task results
remain inspectable. No overall score is published until all five tasks finish.

## Validation and limitations

Reference programs are author-written harness fixtures, never model responses
or model scores. All 60 literal cases are checked against these fixtures. Two
independent Python exhaustive oracles also check the new reference programs on
140 seeded small graphs and scheduling inputs. A separate zero-duration prefix
case exercises critical-path tie-breaking. A greedy scheduler demonstrably earns
10 where the expected optimum is 12. A graph walker without memoization exceeds
the execution limit on the layered case.

These checks establish specific failure cases for shortcuts; they do not show
how any particular model performs. There are no v1.3 model attempts yet. GPT-6
Sol's rejected v1.2 call remains in its original archive, unscored. The local
catalog lists its lowest effort as `low`, but that does not prove account access.

The cases are public and non-exhaustive. Passing them is not evidence of general
coding competence or resistance to memorization. CPU limits vary in practice
with interpreter and hardware performance. Timings include the Codex harness.
Keep all these limits visible when comparing repeated runs.

## Reproduce and publish

```sh
.venv/bin/python -m pip install -r requirements-v1.3.txt
codex login status
.venv/bin/python bench_v1_3.py --model codex-cli/<model-id> --dry-run
.venv/bin/python bench_v1_3.py --model codex-cli/<model-id> \
  --output runs/v1.3/YYYY-MM-DD-<model>-r1.json
.venv/bin/python web/scripts/sync-everyday-v1.3-data.py
.venv/bin/python -m unittest discover -s tests
npm --prefix web run lint
npm --prefix web run build
cd web
vercel --prod --yes
```

Save each attempt to a new file. The exporter verifies version, source hash,
prompts, effort policy, budgets and scoring, and regrades completed responses.
The active API is `/api/v1.3/results`. Version 1.2's source, artifact, API and
36-check meaning are frozen at `/archive/v1.2`; v1.1 and legacy evidence remain
unchanged. Do not relabel an older score or merge it into the 60-check total.
Commit source, artifacts and generated data together. After publication, the
next substantive contract, case, scoring or budget change needs a new version.
