"""Export verified v1.1 artifacts and oracle-backed demos for the static site."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench_v1_1 import suite_fingerprint
from counterexample_lab.grader import grade
from counterexample_lab.ledger import MUTANTS, replay
from providers import display_name

FAULTS = [
    ("Lost request history", "A restart forgets which requests already ran.", "Recovery"),
    ("Forgotten rejection", "Only successful requests keep their original result.", "Idempotency"),
    ("Unchecked payload", "A reused ID accepts different transfer arguments.", "Identity"),
    ("Revalidated retry", "A retry is checked against state it already changed.", "Idempotency"),
    ("Partial transfer", "A rejected transfer still removes money from its source.", "Atomicity"),
    ("Missing revision", "Receiving money does not advance the destination revision.", "Versioning"),
    ("Stale write", "A transfer is accepted with an outdated source revision.", "Versioning"),
    ("Overwritten history", "A conflicting request replaces the original cached result.", "Identity"),
]


def transfer(destination="b"):
    return {"op": "transfer", "id": "payment-1", "from": "a", "to": destination,
            "amount": 3, "expected_revision": 0}


demo_specs = [
    {
        "id": "retry", "title": "An identical retry", "mutant": "revalidate_duplicate",
        "description": "Same request. Same result. Even after the balance changes.",
        "explanation": "The first transfer advanced A's revision. A retry must return its cached success. The faulty ledger validates it again and rejects it as stale.",
        "events": [transfer(), transfer()],
        "labels": ["Transfer 3 from A to B", "Retry the exact same request"],
    },
    {
        "id": "recovery", "title": "A restart in between", "mutant": "forget_cache_on_restart",
        "description": "Request history is part of the state that has to survive.",
        "explanation": "Restarting must preserve the result of payment-1. This faulty ledger loses the cache and treats the retry as a new, stale request.",
        "events": [transfer(), {"op": "restart"}, transfer()],
        "labels": ["Transfer 3 from A to B", "Restart the ledger", "Retry payment-1"],
    },
    {
        "id": "atomicity", "title": "A transfer that fails", "mutant": "debit_before_credit_validation",
        "description": "An error response should not hide a change to the balance.",
        "explanation": "Both ledgers reject the unknown destination. Inspecting the state exposes the bug: the faulty ledger deducted 3 anyway. A rejection must leave all balances unchanged.",
        "events": [transfer("missing"), {"op": "inspect"}],
        "labels": ["Transfer to an unknown account", "Inspect the balances"],
    },
]
def build_data(run_dir: Path | None = None):
    demos = []
    for spec in demo_specs:
        events = spec["events"]
        expected = replay(events)
        actual = replay(events, spec["mutant"])
        steps = [{
            "label": spec["labels"][i], "event": event,
            "expected": expected[i], "actual": actual[i],
            "state": replay(events[:i + 1] + [{"op": "inspect"}])[-1],
            "faultyState": replay(events[:i + 1] + [{"op": "inspect"}], spec["mutant"])[-1],
            "differs": expected[i] != actual[i],
        } for i, event in enumerate(events)]
        demos.append({key: value for key, value in spec.items() if key not in ("events", "labels")} | {"steps": steps})

    fingerprint = suite_fingerprint()
    runs = []
    for path in sorted((run_dir or ROOT / "runs/v1.1").glob("*.json")):
        artifact = json.loads(path.read_text())
        if artifact.get("source") != "subscription":
            continue  # Hand-authored/offline fixtures are never model measurements.
        if artifact.get("benchmark_version") != "1.1" or artifact.get("suite_sha256") != fingerprint:
            raise ValueError(f"Incompatible suite in {path.name}; separate calibration cohorts")
        if artifact.get("prompt") != (ROOT / "counterexample_lab/prompt.md").read_text():
            raise ValueError(f"Prompt mismatch: {path.name}")
        if artifact.get("status") not in {"completed", "failed"}:
            raise ValueError(f"Unknown run status: {path.name}")
        if not artifact["model"].startswith("codex-cli/"):
            raise ValueError(f"Non-subscription model: {path.name}")
        if artifact["status"] == "completed":
            if grade(artifact["response"]) != artifact["score"]:
                raise ValueError(f"Stored score does not reproduce: {path.name}")
        elif artifact.get("score") is not None:
            raise ValueError(f"Failed call has a score: {path.name}")
        runs.append({"id": path.stem, "modelName": display_name(artifact["model"]).removesuffix(" (Codex CLI)"), **artifact})

    settings = {(run["reasoning_effort"], run["output_token_target"]) for run in runs}
    if len(settings) > 1:
        raise ValueError("Mixed effort or output targets; export separate calibration cohorts")

    models = []
    for model_id in sorted({run["model"] for run in runs}):
        attempts = [run for run in runs if run["model"] == model_id]
        completed = [run for run in attempts if run["status"] == "completed"]
        efforts = {run["reasoning_effort"] for run in attempts}
        if len(efforts) != 1:
            raise ValueError(f"Mixed reasoning settings for {model_id}; separate calibration cohorts")
        scores = [run["score"]["killed"] for run in completed]
        models.append({
            "id": model_id, "name": display_name(model_id).removesuffix(" (Codex CLI)"), "effort": next(iter(efforts)),
            "attempts": len(attempts), "completed": len(completed),
            "failed": len(attempts) - len(completed), "scores": scores,
            "runIds": [run["id"] for run in attempts],
            "faultCoverage": {fault: sum(fault in run["score"]["killed_mutants"] for run in completed)
                              for fault in MUTANTS},
        })

    data = {
        "version": "1.1", "suiteHash": fingerprint,
        "lastRunAt": max((run["generated_at"] for run in runs), default=None),
        "calibrationReady": len(models) >= 2 and all(model["completed"] >= 3 and model["failed"] == 0 for model in models),
        "prompt": (ROOT / "counterexample_lab/prompt.md").read_text(),
        "faults": [{"id": identifier, "name": name, "description": description, "family": family}
                   for identifier, (name, description, family) in zip(MUTANTS, FAULTS)],
        "demos": demos, "models": models, "runs": runs,
    }
    return data


if __name__ == "__main__":
    data = build_data()
    target = ROOT / "web/data/counterexample.json"
    target.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Exported {len(data['runs'])} verified attempts and {len(data['demos'])} oracle-backed examples to {target}")
