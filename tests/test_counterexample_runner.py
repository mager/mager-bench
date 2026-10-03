import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import bench_v1_1 as runner
from challenges import CHALLENGES


INSPECT = json.dumps({"traces": [{"events": [{"op": "inspect"}], "expected": [
    {"balances": {"a": 10, "b": 0, "c": 0},
     "revisions": {"a": 0, "b": 0, "c": 0}}
]}]})


class RunnerTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.runs = self.root / "runs"
        self.destination = self.runs / "attempt.json"
        self.enterContext(patch.object(runner, "RUNS", self.runs))
        self.stdout = self.enterContext(contextlib.redirect_stdout(io.StringIO()))
        self.enterContext(contextlib.redirect_stderr(io.StringIO()))

    def args(self):
        return ["--model", "codex-cli/gpt-6-astra", "--reasoning-effort", "ultra",
                "--output", str(self.destination)]

    def artifact(self):
        return json.loads(self.destination.read_text())

    @patch("providers.is_configured")
    @patch("providers.get_provider")
    def test_dry_run_never_calls_provider_or_authentication(self, provider, configured):
        self.assertEqual(runner.main(self.args() + ["--dry-run"]), 0)
        provider.assert_not_called()
        configured.assert_not_called()
        self.assertIn("1 subject calls + 0 judge calls", self.stdout.getvalue())
        self.assertFalse(self.destination.exists())

    @patch("providers.is_configured", return_value=True)
    @patch("providers.get_provider")
    def test_subscription_artifact_preserves_response_effort_and_contract(self, provider, _):
        provider.return_value = Mock()
        provider.return_value.complete.return_value = INSPECT
        self.assertEqual(runner.main(self.args()), 0)
        artifact = self.artifact()
        self.assertEqual(artifact["status"], "completed")
        self.assertEqual(artifact["response"], INSPECT)
        self.assertEqual(artifact["reasoning_effort"], "ultra")
        self.assertEqual(artifact["suite_sha256"], runner.suite_fingerprint())
        self.assertEqual(artifact["prompt"], runner.PROMPT.read_text())
        self.assertEqual(artifact["score"]["killed"], 0)
        self.assertNotIn("results", artifact)
        self.assertNotIn("judge", artifact)
        provider.assert_called_once_with("codex-cli/gpt-6-astra", reasoning_effort="ultra")

    @patch("providers.is_configured", return_value=True)
    @patch("providers.get_provider")
    def test_provider_failure_saved_unscored(self, provider, _):
        provider.return_value.complete.side_effect = RuntimeError("connection interrupted")
        self.assertEqual(runner.main(self.args()), 1)
        self.assertEqual(self.artifact()["status"], "failed")
        self.assertIsNone(self.artifact()["score"])
        self.assertIn("connection interrupted", self.artifact()["error"])

    def test_malformed_offline_response_saved_unscored(self):
        submission = self.root / "submission.json"
        submission.write_text('{"traces": [{"events": [{"op": "inspect"}], '
                              '"expected": [{"value": 1e9999}]}]}')
        self.assertEqual(runner.main(["--submission", str(submission), "--output",
                                      str(self.destination)]), 1)
        self.assertEqual(self.artifact()["response"], submission.read_text())
        self.assertEqual(self.artifact()["source"], "offline")
        self.assertIsNone(self.artifact()["model"])
        self.assertIsNone(self.artifact()["score"])

    @patch("providers.get_provider")
    def test_refuses_existing_output_before_a_call(self, provider):
        self.runs.mkdir()
        self.destination.write_text("original evidence")
        with self.assertRaises(SystemExit):
            runner.main(self.args())
        self.assertEqual(self.destination.read_text(), "original evidence")
        provider.assert_not_called()

    def test_refuses_legacy_board_and_api_subject(self):
        with self.assertRaisesRegex(ValueError, "runs/v1.1"):
            runner.output_path(str(runner.ROOT / "results.json"))
        with self.assertRaises(SystemExit):
            runner.main(["--model", "gpt-4o-mini", "--dry-run"])

    def test_suite_manifest_preserves_all_legacy_prompts(self):
        manifest = json.loads((runner.ROOT / "benchmark-suites.json").read_text())
        self.assertEqual(manifest["current_version"], "1.3")
        self.assertEqual(manifest["suites"]["1.1"]["challenges"], ["counterexample-ledger"])
        self.assertEqual(manifest["suites"]["legacy-13"]["challenges"],
                         [challenge.name for challenge in CHALLENGES])


if __name__ == "__main__":
    unittest.main()
