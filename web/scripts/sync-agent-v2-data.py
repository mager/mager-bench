"""Regrade v2 artifacts and export the site index plus exact downloadable evidence."""

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agent_bench_v2.evidence import validate
from agent_bench_v2.runner import fingerprint
from agent_bench_v2.tasks import TASKS, PHASE_SECONDS, RUN_SECONDS, LEVELS, prompt


def export(check=False):
    runs = []
    copies = []
    for path in sorted((ROOT / "runs/v2").glob("*.json")):
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", path.stem):
            raise ValueError("Unsafe artifact filename")
        raw = path.read_text()
        run = json.loads(raw)
        if run.get("status") == "running":
            print(f"Not published: {path.name} is still running.")
            continue
        validate(run)
        row = {
            k: run.get(k)
            for k in (
                "kind",
                "model",
                "reasoning_effort",
                "seed",
                "level",
                "suite_sha256",
                "generated_at",
                "status",
                "score",
                "elapsed_ms",
                "generation_ms",
                "runtime",
                "error",
            )
        }
        row.update(
            id=path.stem,
            raw_url=f"/evidence/v2/{path.name}",
            tasks=[],
            probe=run.get("probe"),
        )
        for task in run["tasks"]:
            phases = []
            for phase in task["phases"]:
                item = {
                    k: phase.get(k)
                    for k in (
                        "phase",
                        "status",
                        "error",
                        "elapsed_ms",
                        "usage",
                        "command_count",
                        "diff",
                        "sources",
                        "response",
                        "integrity_errors",
                    )
                }
                score = phase.get("score")
                item["score"] = (
                    None
                    if score is None
                    else {
                        "passed": score["passed"],
                        "total": score["total"],
                        "groups": {
                            group: {
                                "passed": sum(
                                    c["passed"]
                                    for c in score["cases"]
                                    if c["group"] == group
                                ),
                                "total": sum(
                                    c["group"] == group for c in score["cases"]
                                ),
                            }
                            for group in sorted({c["group"] for c in score["cases"]})
                        },
                        "failures": [c for c in score["cases"] if not c["passed"]][:3],
                    }
                )
                phases.append(item)
            row["tasks"].append(dict(id=task["id"], phases=phases))
        runs.append(row)
        copies.append((path.name, raw))
    data = dict(
        version="2.0",
        suite_sha256=fingerprint(),
        phase_seconds=PHASE_SECONDS,
        budget_seconds=RUN_SECONDS,
        checks=192,
        levels={
            str(k): dict(entities=v[0], operations=v[1]) for k, v in LEVELS.items()
        },
        tasks=[
            dict(
                **t,
                prompts=[prompt(t["id"], p) for p in (1, 2)],
                starter={
                    "src/index.js": 'module.exports = require("./engine.js");\n',
                    "src/engine.js": (
                        ROOT / "agent_bench_v2/templates" / f"{t['id']}.js"
                    ).read_text(),
                },
            )
            for t in TASKS
        ],
        runs=sorted(runs, key=lambda r: r["generated_at"], reverse=True),
    )
    # Validate every artifact before writing any published file.
    destination = ROOT / "web/public/evidence/v2"
    outputs = {destination / name: raw for name, raw in copies}
    outputs[ROOT / "web/data/agent-v2.json"] = json.dumps(data, indent=2) + "\n"
    stale = set(destination.glob("*.json")) - set(outputs)
    mismatches = [
        path
        for path, content in outputs.items()
        if not path.is_file() or path.read_bytes() != content.encode()
    ]
    if check:
        if stale or mismatches:
            paths = sorted(
                path.relative_to(ROOT).as_posix() for path in stale | set(mismatches)
            )
            raise ValueError(
                "Generated evidence is missing, changed, or stale: " + ", ".join(paths)
            )
        print(
            f"Verified {len(runs)} saved attempts and exact generated files; no files changed."
        )
        return
    if stale:
        raise ValueError(
            "Unexpected evidence files; restore their source artifacts or remove stale generated copies: "
            + ", ".join(sorted(p.name for p in stale))
        )
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    print(f"Exported {len(runs)} saved attempts; completed phases regraded.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Regrade and verify generated files without writing",
    )
    export(check=parser.parse_args().check)
