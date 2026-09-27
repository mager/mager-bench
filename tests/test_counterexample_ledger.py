"""Hand-derived contract examples and independently witnessed ledger faults."""

from copy import deepcopy

import unittest

from counterexample_lab import MUTANTS, replay


def transfer(request_id="x", source="a", destination="b", amount=3, revision=0):
    return {"op": "transfer", "id": request_id, "from": source,
            "to": destination, "amount": amount, "expected_revision": revision}


def state(balances=(10, 0, 0), revisions=(0, 0, 0)):
    return {"balances": dict(zip("abc", balances)),
            "revisions": dict(zip("abc", revisions))}


WITNESSES = {
    "forget_cache_on_restart": [transfer(), {"op": "restart"}, transfer()],
    "cache_success_only": [transfer(destination="missing"), transfer()],
    "ignore_conflicting_payload": [transfer(), transfer(amount=4)],
    "revalidate_duplicate": [transfer(), transfer()],
    "debit_before_credit_validation": [transfer(destination="missing"), {"op": "inspect"}],
    "no_destination_revision": [transfer(), {"op": "inspect"}],
    "accept_stale_revision": [transfer(revision=1)],
    "conflict_overwrites_cache": [transfer(), transfer(amount=4), transfer()],
}

EXPECTED_MUTANT_OUTPUTS = {
    "forget_cache_on_restart": [{"status": "ok"}, {"status": "restarted"}, {"status": "stale_revision"}],
    "cache_success_only": [{"status": "unknown_account"}, {"status": "ok"}],
    "ignore_conflicting_payload": [{"status": "ok"}, {"status": "ok"}],
    "revalidate_duplicate": [{"status": "ok"}, {"status": "stale_revision"}],
    "debit_before_credit_validation": [{"status": "unknown_account"}, state((7, 0, 0))],
    "no_destination_revision": [{"status": "ok"}, state((7, 3, 0), (1, 0, 0))],
    "accept_stale_revision": [{"status": "ok"}],
    "conflict_overwrites_cache": [{"status": "ok"}, {"status": "conflict"}, {"status": "conflict"}],
}


class LedgerContractTests(unittest.TestCase):
    def test_success_duplicate_and_restart_preserve_balances_revisions_and_history(self):
        request = transfer()
        events = [{"op": "inspect"}, request, {"op": "inspect"},
                  {"op": "restart"}, request, {"op": "inspect"}]
        self.assertEqual(replay(events), [
            state(), {"status": "ok"}, state((7, 3, 0), (1, 1, 0)),
            {"status": "restarted"}, {"status": "ok"},
            state((7, 3, 0), (1, 1, 0)),
        ])

    def test_rejected_request_stays_rejected_after_balance_and_revision_change(self):
        rejected = transfer("debit", "b", "c", 1)
        self.assertEqual(replay([rejected, transfer("fund", amount=3), rejected,
                       {"op": "inspect"}]), [
            {"status": "insufficient_funds"}, {"status": "ok"},
            {"status": "insufficient_funds"}, state((7, 3, 0), (1, 1, 0)),
        ])

    def test_conflict_neither_replaces_original_request_nor_changes_state(self):
        request = transfer()
        conflict = transfer(amount=4)
        self.assertEqual(replay([request, conflict, conflict, request, {"op": "inspect"}]), [
            {"status": "ok"}, {"status": "conflict"}, {"status": "conflict"},
            {"status": "ok"}, state((7, 3, 0), (1, 1, 0)),
        ])

    def test_validation_order_and_rejection_atomicity(self):
        cases = [
            (transfer(source="missing", destination="missing", revision=3), "unknown_account"),
            (transfer(source="b", destination="missing", revision=3), "unknown_account"),
            (transfer(source="b", destination="b", revision=3), "same_account"),
            (transfer(source="b", destination="c", revision=3), "stale_revision"),
            (transfer(source="b", destination="c"), "insufficient_funds"),
        ]
        for request, status in cases:
            with self.subTest(request=request):
                self.assertEqual(replay([request, {"op": "inspect"}]), [{"status": status}, state()])

    def test_rejected_request_also_owns_its_id_and_survives_restart(self):
        rejected = transfer(destination="missing")
        self.assertEqual(replay([rejected, {"op": "restart"}, transfer(), rejected,
                       {"op": "inspect"}]), [
            {"status": "unknown_account"}, {"status": "restarted"},
            {"status": "conflict"}, {"status": "unknown_account"}, state(),
        ])

    def test_each_transfer_argument_is_part_of_fingerprint(self):
        for field, value in [("from", "c"), ("to", "c"), ("amount", 4), ("expected_revision", 1)]:
            with self.subTest(field=field):
                changed = {**transfer(), field: value}
                self.assertEqual(replay([transfer(), changed]), [{"status": "ok"}, {"status": "conflict"}])

    def test_destination_revision_is_used_when_it_later_becomes_a_source(self):
        self.assertEqual(replay([transfer(), transfer("spend", "b", "c", 2, 1),
                       {"op": "inspect"}]), [
            {"status": "ok"}, {"status": "ok"}, state((7, 1, 2), (1, 2, 1)),
        ])

    def test_results_and_calls_are_independent_and_input_is_unchanged(self):
        events = [transfer(), transfer(), {"op": "inspect"}, {"op": "inspect"}]
        original = deepcopy(events)
        outputs = replay(events)
        outputs[0]["status"] = "modified"
        outputs[2]["balances"]["a"] = 100
        self.assertEqual(outputs[1], {"status": "ok"})
        self.assertEqual(outputs[3], state((7, 3, 0), (1, 1, 0)))
        self.assertEqual(events, original)
        self.assertEqual(replay([{"op": "inspect"}]), [state()])
        self.assertEqual(replay([]), [])


    def test_each_mutant_has_a_distinguishing_trace(self):
        for mutant in MUTANTS:
            with self.subTest(mutant=mutant):
                actual = replay(WITNESSES[mutant], mutant=mutant)
                self.assertEqual(actual, EXPECTED_MUTANT_OUTPUTS[mutant])
                self.assertNotEqual(actual, replay(WITNESSES[mutant]))

    def test_mutants_still_obey_unrelated_base_case(self):
        # These events trigger none of the eight defects.
        events = [{"op": "inspect"}, transfer(source="missing"),
                  {"op": "restart"}, {"op": "inspect"}]
        for mutant in MUTANTS:
            with self.subTest(mutant=mutant):
                self.assertEqual(replay(events, mutant=mutant), [
                    state(), {"status": "unknown_account"}, {"status": "restarted"}, state(),
                ])

    def test_unknown_mutant_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown mutant"):
            replay([], mutant="typo")


if __name__ == "__main__":
    unittest.main()
