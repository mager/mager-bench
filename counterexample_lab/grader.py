"""Score regression data, never execute model-authored code."""

from __future__ import annotations

import json
import math
import re
from typing import Any

from .ledger import MUTANTS, replay

VERSION = "1.1"
EVENT_BUDGET = 12
MAX_RESPONSE_BYTES = 64_000


class SubmissionError(ValueError):
    """Malformed or out-of-budget submissions are unscored, not zeroes."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise SubmissionError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise SubmissionError(f"non-JSON numeric constant: {value}")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise SubmissionError("numeric overflow in JSON")
    return number


def _keys(value: Any, keys: set[str], label: str) -> None:
    if not isinstance(value, dict) or set(value) != keys:
        raise SubmissionError(f"{label} must contain exactly {sorted(keys)}")


def parse_submission(response: str) -> dict:
    if not response.strip() or len(response.encode()) > MAX_RESPONSE_BYTES:
        raise SubmissionError("empty or oversized response")
    try:
        data = json.loads(response, object_pairs_hook=_unique_object,
                          parse_constant=_reject_constant, parse_float=_finite_float)
    except (ValueError, RecursionError) as exc:
        raise SubmissionError(f"invalid JSON: {exc}") from exc
    _keys(data, {"traces"}, "submission")
    traces = data["traces"]
    if not isinstance(traces, list) or not 1 <= len(traces) <= 4:
        raise SubmissionError("provide 1–4 traces")
    total = 0
    for index, trace in enumerate(traces):
        _keys(trace, {"events", "expected"}, f"trace {index}")
        events, expected = trace["events"], trace["expected"]
        if not isinstance(events, list) or not events:
            raise SubmissionError(f"trace {index} needs nonempty events")
        if not isinstance(expected, list) or len(expected) != len(events):
            raise SubmissionError(f"trace {index} needs one expected output per event")
        if any(not isinstance(output, dict) for output in expected):
            raise SubmissionError("expected outputs must be JSON objects")
        total += len(events)
        for event in events:
            if not isinstance(event, dict):
                raise SubmissionError("events must be objects")
            op = event.get("op")
            if op in ("inspect", "restart"):
                _keys(event, {"op"}, "event")
                continue
            if op != "transfer":
                raise SubmissionError("unknown event operation")
            _keys(event, {"op", "id", "from", "to", "amount", "expected_revision"},
                  "transfer")
            if not isinstance(event["id"], str) or not re.fullmatch(
                r"[A-Za-z0-9_-]{1,24}", event["id"]
            ):
                raise SubmissionError("invalid request ID")
            if any(event[key] not in ("a", "b", "c", "missing") for key in ("from", "to")):
                raise SubmissionError("unknown account label; use 'missing' to test rejection")
            for key, low in (("amount", 1), ("expected_revision", 0)):
                if type(event[key]) is not int or not low <= event[key] <= 20:
                    raise SubmissionError(f"{key} must be an integer {low}–20")
    if total > EVENT_BUDGET:
        raise SubmissionError(f"event budget exceeded: {total} > {EVENT_BUDGET}")
    return data


def _canonical(value: Any) -> str:
    # Python equality equates True with 1 and 1.0: JSON serialization does not.
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def grade(response: str) -> dict:
    submission = parse_submission(response)
    killed: set[str] = set()
    details = []
    for index, trace in enumerate(submission["traces"]):
        expected = trace["expected"]
        actual = replay(trace["events"])
        mismatch = next((i for i, (a, b) in enumerate(zip(expected, actual))
                         if _canonical(a) != _canonical(b)), None)
        trace_kills = []
        if mismatch is None:
            for mutant in MUTANTS:
                if _canonical(replay(trace["events"], mutant)) != _canonical(expected):
                    trace_kills.append(mutant)
            killed.update(trace_kills)
        details.append({"index": index, "oracle_match": mismatch is None,
                        "first_mismatch": mismatch, "killed_mutants": trace_kills})
    return {
        "benchmark_version": VERSION,
        "challenge": "counterexample-ledger",
        "scorer": "mutation-v1",
        "event_budget": EVENT_BUDGET,
        "events_used": sum(len(t["events"]) for t in submission["traces"]),
        "valid_traces": sum(d["oracle_match"] for d in details),
        "total_traces": len(details),
        "killed": len(killed),
        "total_mutants": len(MUTANTS),
        "mutation_score": len(killed) / len(MUTANTS),
        "killed_mutants": [m for m in MUTANTS if m in killed],
        "surviving_mutants": [m for m in MUTANTS if m not in killed],
        "trace_results": details,
    }
