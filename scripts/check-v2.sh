#!/bin/sh
# Local checks only. No model calls, account access, or generated scores.
set -eu
cd "$(dirname "$0")/.."
BENCH_PYTHON="${BENCH_PYTHON:-.venv/bin/python}"
"$BENCH_PYTHON" -m ruff check agent_bench_v2 bench_v2.py tests/test_agent_bench_v2.py web/scripts/sync-agent-v2-data.py
"$BENCH_PYTHON" -m unittest discover -s tests
"$BENCH_PYTHON" web/scripts/sync-agent-v2-data.py --check
npm --prefix web run check
