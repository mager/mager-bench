"""A durable ledger oracle and eight deliberately defective variants.

Inputs are schema-validated by the caller. Restart simulates loading committed
state, including request history; this is not a filesystem durability test.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

MUTANTS = (
    "forget_cache_on_restart",
    "cache_success_only",
    "ignore_conflicting_payload",
    "revalidate_duplicate",
    "debit_before_credit_validation",
    "no_destination_revision",
    "accept_stale_revision",
    "conflict_overwrites_cache",
)


class _Ledger:
    def __init__(self, mutant: str | None) -> None:
        self.mutant = mutant
        self.balances = {"a": 10, "b": 0, "c": 0}
        self.revisions = {"a": 0, "b": 0, "c": 0}
        self.cache: dict[str, tuple[tuple, dict]] = {}

    def _validate(self, event: dict[str, Any]) -> str:
        source, destination = event["from"], event["to"]
        if source not in self.balances or destination not in self.balances:
            return "unknown_account"
        if source == destination:
            return "same_account"
        if (self.mutant != "accept_stale_revision"
                and event["expected_revision"] != self.revisions[source]):
            return "stale_revision"
        if self.balances[source] < event["amount"]:
            return "insufficient_funds"
        return "ok"

    def apply(self, event: dict[str, Any]) -> dict:
        operation = event["op"]
        if operation == "inspect":
            return deepcopy({"balances": self.balances, "revisions": self.revisions})
        if operation == "restart":
            self.balances, self.revisions, self.cache = deepcopy(
                (self.balances, self.revisions, self.cache)
            )
            if self.mutant == "forget_cache_on_restart":
                self.cache.clear()
            return {"status": "restarted"}
        if operation != "transfer":
            raise ValueError(f"Unknown operation: {operation}")

        request_id = event["id"]
        source, destination = event["from"], event["to"]
        fingerprint = (source, destination, event["amount"], event["expected_revision"])
        if request_id in self.cache:
            original, result = self.cache[request_id]
            if self.mutant == "ignore_conflicting_payload":
                return deepcopy(result)
            if fingerprint != original:
                conflict = {"status": "conflict"}
                if self.mutant == "conflict_overwrites_cache":
                    self.cache[request_id] = (fingerprint, deepcopy(conflict))
                return conflict
            if self.mutant == "revalidate_duplicate":
                status = self._validate(event)
                if status != "ok":
                    return {"status": status}
            return deepcopy(result)

        status = self._validate(event)
        if (self.mutant == "debit_before_credit_validation"
                and destination not in self.balances
                and source in self.balances
                and source != destination
                and event["expected_revision"] == self.revisions[source]
                and self.balances[source] >= event["amount"]):
            self.balances[source] -= event["amount"]
        if status == "ok":
            self.balances[source] -= event["amount"]
            self.balances[destination] += event["amount"]
            self.revisions[source] += 1
            if self.mutant != "no_destination_revision":
                self.revisions[destination] += 1
        result = {"status": status}
        if self.mutant != "cache_success_only" or status == "ok":
            self.cache[request_id] = (fingerprint, deepcopy(result))
        return result


def replay(events: list[dict], mutant: str | None = None) -> list[dict]:
    """Return one observable output per event from an independent fresh ledger."""
    if mutant is not None and mutant not in MUTANTS:
        raise ValueError(f"Unknown mutant: {mutant}")
    ledger = _Ledger(mutant)
    return [ledger.apply(event) for event in events]
