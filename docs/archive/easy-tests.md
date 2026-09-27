# Retired easy tasks

mager-bench 1.1 retires these tasks from its active suite:

| Task | Original scope |
|---|---|
| `fizzbuzz` | Basic branching, a docstring, and a usage example |
| `binary-search` | A familiar search algorithm with documentation |
| `refactor` | Rename and simplify a short loop while preserving behavior |

These narrow, familiar exercises are less useful for the next round of testing
than stateful counterexamples. Retirement is a scope decision, not a claim that
every model has solved every task. One high-scoring run does not establish that.

The [original challenge definitions](../../challenges.py),
[saved board results](../../results.json), and [source runs](../../runs/) remain
available. The frozen `legacy-13` suite still runs through
[`bench.py`](../../bench.py) with all thirteen original tasks. Nothing has been
removed from historical averages or relabeled as a new benchmark version.

The remaining ten legacy tasks are available as optional baselines: `api-client`,
`readme-writer`, `test-writing`, `debug`, `async-fetch`, `sql`, `go-test`,
`elixir-test`, `doom`, and `slots`. Their old scoring contract stays separate.

[Counterexample Lab](../mager-bench-1.1.md) is the first active 1.1 track. The
[suite manifest](../../benchmark-suites.json) records the active and frozen
memberships. New results must identify their suite; never blend the ledger's
fault-coverage score with legacy model-judge scores.
