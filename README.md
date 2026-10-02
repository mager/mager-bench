# mager-bench

A quick test of useful code. [Live site](https://bench.mager.co/).

Version 1.2 asks a model for three JavaScript programs: split a bill, clean a
contact CSV, and find a meeting time. The contracts include weighted refunds,
quoted multiline records, duplicate merging, time zones, and schedule buffers.
Twelve exact checks per task produce a count out of 36. There are no LLM judges.

All evals use the lowest supported reasoning effort. Three calls maximum,
90-second deadline per call, 3,072-token prompted output target. Programs run in
bounded QuickJS contexts without host I/O. ChatGPT subscription only.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-v1.2.txt
codex login status
.venv/bin/python bench_v1_2.py --model codex-cli/gpt-6-sol --dry-run
.venv/bin/python bench_v1_2.py --model codex-cli/gpt-6-sol \
  --output runs/v1.2/YYYY-MM-DD-gpt-6-sol-r1.json
```

GPT-6 Sol's first attempt on October 2 was rejected by the subscription CLI.
It is saved and unscored. A catalog entry does not guarantee account access.

- [Exact contracts and public cases](everyday_v1_2/tasks.py)
- [Protocol, limitations, and publishing](docs/mager-bench-1.2.md)
- [Saved attempts](runs/v1.2/)
- [Canonical agent workflow](.opencode/commands/bench.md)

Run `.venv/bin/python -m unittest discover -s tests` to check the harness. The
fixture programs are author-written test code, never model results.

## Historical suites

Counterexample Lab 1.1 and the original thirteen-task suite are frozen.
Their prompts, artifacts, judges, scores, and APIs retain their original meanings.
See [1.1 documentation](docs/mager-bench-1.1.md) and the
[site archive](https://bench.mager.co/archive). Do not merge scores across suites.
