"""Publication rejects incompatible or altered evidence without editing artifacts."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("site_export", ROOT / "web/scripts/sync-counterexample-data.py")
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class SiteExportTests(unittest.TestCase):
    def setUp(self):
        self.sample = json.loads((ROOT / "runs/v1.1/2026-09-30-codex-cli-gpt-6-astra-r1.json").read_text())

    def export(self, artifacts):
        with tempfile.TemporaryDirectory() as directory:
            for index, artifact in enumerate(artifacts):
                Path(directory, f"run-{index}.json").write_text(json.dumps(artifact))
            return exporter.build_data(Path(directory))

    def test_saved_cohort_regrades_and_keeps_every_attempt(self):
        artifacts = [json.loads(path.read_text()) for path in sorted((ROOT / "runs/v1.1").glob("2026-09-30-*.json"))]
        data = self.export(artifacts)
        self.assertTrue(data["calibrationReady"])
        self.assertEqual(len(data["runs"]), 6)
        self.assertEqual({m["id"]: m["scores"] for m in data["models"]}, {
            "codex-cli/gpt-6-astra": [7, 7, 7],
            "codex-cli/gpt-5.6-sol": [7, 6, 5],
        })

    def test_tampered_score_hash_prompt_and_status_rejected(self):
        mutations = [
            lambda a: a["score"].update(killed=8),
            lambda a: a.update(suite_sha256="different"),
            lambda a: a.update(prompt="different"),
            lambda a: a.update(status="pending"),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                artifact = copy.deepcopy(self.sample)
                mutate(artifact)
                with self.assertRaises(ValueError):
                    self.export([artifact])

    def test_mixed_settings_rejected_across_models(self):
        for field, value in [("reasoning_effort", "high"), ("output_token_target", 2048)]:
            with self.subTest(field=field):
                artifact = copy.deepcopy(self.sample)
                artifact.update(model="codex-cli/gpt-5.6-sol")
                artifact[field] = value
                with self.assertRaises(ValueError):
                    self.export([self.sample, artifact])

    def test_failed_call_retained_unscored_and_fixture_excluded(self):
        failed = copy.deepcopy(self.sample)
        failed.update(status="failed", score=None, response="")
        fixture = copy.deepcopy(self.sample)
        fixture.update(source="offline")
        data = self.export([failed, fixture])
        self.assertFalse(data["calibrationReady"])
        self.assertEqual(len(data["runs"]), 1)
        self.assertIsNone(data["runs"][0]["score"])
        self.assertEqual(data["models"][0]["scores"], [])
        self.assertEqual(data["models"][0]["failed"], 1)
        failed["score"] = self.sample["score"]
        with self.assertRaises(ValueError):
            self.export([failed])

    def test_demo_exposes_state_corruption_after_inspection(self):
        demo = next(d for d in self.export([])["demos"] if d["id"] == "atomicity")
        self.assertFalse(demo["steps"][0]["differs"])
        self.assertTrue(demo["steps"][1]["differs"])
        self.assertEqual(demo["steps"][1]["expected"]["balances"]["a"], 10)
        self.assertEqual(demo["steps"][1]["actual"]["balances"]["a"], 7)
