# mager-bench

A quick test of useful code. [Live site](https://bench.mager.co/).

Version 1.3 combines two algorithmic problems with three everyday programs:
dependency-graph planning, exact budgeted job scheduling, weighted bill
settlement, CSV cleanup, and meeting-time search. Twelve checks per task give
a count out of 60. Cases include greedy traps and inputs that rule out naive
exhaustive search. There are no LLM judges.

All evals use the lowest supported reasoning effort. Five calls share a
270-second generation waiting budget, with a 90-second deadline per call and
a 3,072-token prompted output target. Programs run in bounded QuickJS contexts
without host I/O. ChatGPT subscription only.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-v1.3.txt
codex login status
.venv/bin/python bench_v1_3.py --model codex-cli/gpt-6-sol --dry-run
.venv/bin/python bench_v1_3.py --model codex-cli/gpt-6-sol \
  --output runs/v1.3/YYYY-MM-DD-gpt-6-sol-r1.json
```

No v1.3 model results are published yet. GPT-6 Sol's first v1.2 attempt on October 2 was rejected by the subscription CLI.
It is saved and unscored. A catalog entry does not guarantee account access.

- [Exact contracts and public cases](everyday_v1_3/tasks.py)
- [Protocol, limitations, and publishing](docs/mager-bench-1.3.md)
- [Saved attempts](runs/v1.3/)
- [Canonical agent workflow](.opencode/commands/bench.md)

Run `.venv/bin/python -m unittest discover -s tests` to check the harness. The
fixture programs are author-written test code, never model results.

## Historical suites

Version 1.2, Counterexample Lab 1.1, and the original thirteen-task suite are frozen.
Their prompts, artifacts, judges, scores, and APIs retain their original meanings.
See [1.1 documentation](docs/mager-bench-1.1.md) and the
[site archive](https://bench.mager.co/archive). Do not merge scores across suites.
