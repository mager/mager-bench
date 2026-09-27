"""Validate counterexample scoring and retained run artifacts without inference."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import bench_v1_1
from counterexample_lab import MUTANTS
from counterexample_lab.grader import SubmissionError, grade, parse_submission


def transfer(request_id="x", source="a", destination="b", amount=3, revision=0):
    return {"op": "transfer", "id": request_id, "from": source,
            "to": destination, "amount": amount, "expected_revision": revision}


def snapshot(balances=(10, 0, 0), revisions=(0, 0, 0)):
    return {"balances": dict(zip("abc", balances)),
            "revisions": dict(zip("abc", revisions))}


def complete_suite():
    """A hand-derived twelve-event witness that makes the budget achievable."""
    rejected = transfer("f", "b", "a", 1)
    request = transfer()
    return {"traces": [
        {"events": [rejected, request, request, rejected, transfer(amount=4),
                    request, {"op": "restart"}, request, {"op": "inspect"}],
         "expected": [
             {"status": "insufficient_funds"}, {"status": "ok"}, {"status": "ok"},
             {"status": "insufficient_funds"}, {"status": "conflict"}, {"status": "ok"},
             {"status": "restarted"}, {"status": "ok"}, snapshot((7, 3, 0), (1, 1, 0)),
         ]},
        {"events": [transfer(destination="missing", amount=1), {"op": "inspect"}],
         "expected": [{"status": "unknown_account"}, snapshot()]},
        {"events": [transfer(amount=1, revision=1)],
         "expected": [{"status": "stale_revision"}]},
    ]}


class CounterexampleGraderTests(unittest.TestCase):
    def test_hand_derived_suite_exposes_all_eight_faults_within_budget(self):
        result = grade(json.dumps(complete_suite()))
        self.assertEqual(result["events_used"], 12)
        self.assertEqual(result["valid_traces"], 3)
        self.assertEqual(result["killed"], 8)
        self.assertEqual(result["mutation_score"], 1.0)
        self.assertEqual(result["killed_mutants"], list(MUTANTS))
        self.assertEqual(result["surviving_mutants"], [])

    def test_one_wrong_expectation_invalidates_coverage_for_the_entire_trace(self):
        trace = complete_suite()["traces"][0]
        trace["expected"][-1]["balances"]["a"] = 8
        result = grade(json.dumps({"traces": [trace]}))
        self.assertEqual(result["killed"], 0)
        self.assertEqual(result["valid_traces"], 0)
        self.assertEqual(result["trace_results"][0]["first_mismatch"], 8)
        self.assertEqual(result["trace_results"][0]["killed_mutants"], [])

    def test_invalid_trace_does_not_discard_a_separate_valid_trace(self):
        data = complete_suite()
        data["traces"][0]["expected"][-1]["balances"]["a"] = 8
        result = grade(json.dumps(data))
        self.assertEqual(result["valid_traces"], 2)
        self.assertEqual(result["killed_mutants"],
                         ["debit_before_credit_validation", "accept_stale_revision"])

    def test_repeated_coverage_counts_each_mutant_only_once(self):
        trace = complete_suite()["traces"][1]
        result = grade(json.dumps({"traces": [trace, deepcopy(trace)]}))
        self.assertEqual(result["valid_traces"], 2)
        self.assertEqual(result["killed"], 1)
        self.assertEqual(result["mutation_score"], 1 / 8)

    def test_boolean_and_float_expected_values_do_not_match_integer_oracle(self):
        for incorrect in (True, 1.0):
            with self.subTest(value=incorrect):
                trace = {"events": [transfer(), {"op": "inspect"}],
                         "expected": [{"status": "ok"}, snapshot((7, 3, 0), (1, 1, 0))]}
                trace["expected"][1]["revisions"]["a"] = incorrect
                result = grade(json.dumps({"traces": [trace]}))
                self.assertEqual(result["killed"], 0)
                self.assertEqual(result["valid_traces"], 0)

    def test_object_key_order_is_irrelevant(self):
        result = grade(json.dumps(complete_suite(), sort_keys=True))
        self.assertEqual(result["killed"], 8)

    def test_submission_schema_errors_are_unscored(self):
        valid = complete_suite()
        variants = ["", "{}", "[]", '{"traces":[],"traces":[]}',
                    '{"traces":NaN}', "[" * 1500 + "]" * 1500,
                    '{"traces":' + "1" * 5000 + "}"]
        for mutate in (
            lambda data: data["traces"][0]["events"][0].update(amount=True),
            lambda data: data["traces"][0]["events"][0].update(expected_revision=0.0),
            lambda data: data["traces"][0]["events"][0].update(extra=1),
            lambda data: data["traces"][0]["events"][0].update(op=[]),
            lambda data: data["traces"][0]["events"][0].update(id="invalid id"),
            lambda data: data["traces"][0]["events"][0].update({"from": []}),
            lambda data: data["traces"][0]["expected"].pop(),
            lambda data: data["traces"][0]["expected"].__setitem__(0, None),
        ):
            data = deepcopy(valid)
            mutate(data)
            variants.append(json.dumps(data))
        for response in variants:
            with self.subTest(response=response[:100]):
                with self.assertRaises(SubmissionError):
                    grade(response)

    def test_thirteenth_event_is_rejected(self):
        data = complete_suite()
        data["traces"].append({"events": [{"op": "inspect"}], "expected": [snapshot()]})
        with self.assertRaisesRegex(SubmissionError, "event budget"):
            grade(json.dumps(data))

    def test_nonfinite_float_from_numeric_overflow_is_unscored(self):
        response = ('{"traces":[{"events":[{"op":"inspect"}],'
                    '"expected":[{"value":1e9999}]}]}')
        with self.assertRaises(SubmissionError):
            grade(response)

    def test_oversized_submission_is_unscored(self):
        with self.assertRaisesRegex(SubmissionError, "oversized"):
            parse_submission(" " * 64_001)


class CounterexampleArtifactTests(unittest.TestCase):
    def run_quietly(self, arguments):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return bench_v1_1.main(arguments)

    def test_offline_success_records_raw_answer_and_exact_suite_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            submission = root / "submission.json"
            response = json.dumps(complete_suite())
            submission.write_text(response)
            output = root / "runs/score.json"
            with patch.object(bench_v1_1, "RUNS", root / "runs"):
                code = self.run_quietly(["--submission", str(submission), "--output", str(output)])
            artifact = json.loads(output.read_text())
            self.assertEqual(code, 0)
            self.assertEqual(artifact["response"], response)
            self.assertEqual(artifact["status"], "completed")
            self.assertEqual(artifact["source"], "offline")
            self.assertIsNone(artifact["model"])
            self.assertEqual(artifact["score"]["killed"], 8)
            self.assertEqual(len(artifact["suite_sha256"]), 64)

    def test_invalid_offline_submission_is_retained_without_a_numeric_score(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            submission = root / "submission.json"
            submission.write_text("malformed json")
            output = root / "runs/failed.json"
            with patch.object(bench_v1_1, "RUNS", root / "runs"):
                code = self.run_quietly(["--submission", str(submission), "--output", str(output)])
            artifact = json.loads(output.read_text())
            self.assertEqual(code, 1)
            self.assertEqual(artifact["response"], "malformed json")
            self.assertEqual(artifact["status"], "failed")
            self.assertIsNone(artifact["score"])

    def test_provider_failure_is_retained_without_a_numeric_score(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "runs/failed.json"
            with (patch.object(bench_v1_1, "RUNS", root / "runs"),
                  patch("providers.is_configured", return_value=True),
                  patch("providers.get_provider") as get_provider):
                get_provider.return_value.complete.side_effect = RuntimeError("test transport failure")
                code = self.run_quietly(["--model", "codex-cli/gpt-6-astra", "--output", str(output)])
            artifact = json.loads(output.read_text())
            self.assertEqual(code, 1)
            self.assertEqual(artifact["status"], "failed")
            self.assertIsNone(artifact["score"])
            self.assertIn("test transport failure", artifact["error"])

    def test_original_board_path_and_prior_artifacts_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "runs/existing.json"
            output.parent.mkdir()
            output.write_text("keep")
            with patch.object(bench_v1_1, "RUNS", root / "runs"):
                with self.assertRaisesRegex(ValueError, "under runs/v1.1"):
                    bench_v1_1.output_path(str(root / "results.json"))
                with self.assertRaisesRegex(ValueError, "already exists"):
                    bench_v1_1.output_path(str(output))
            self.assertEqual(output.read_text(), "keep")

    def test_dry_run_never_acquires_a_provider(self):
        with patch("providers.get_provider") as get_provider:
            code = self.run_quietly(["--model", "codex-cli/gpt-6-astra", "--dry-run"])
        self.assertEqual(code, 0)
        get_provider.assert_not_called()


if __name__ == "__main__":
    unittest.main()
