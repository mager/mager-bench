"""Supplementary subjects must use the frozen subscription transport."""

import unittest
from unittest.mock import patch

from bench_v1_1 import suite_fingerprint
import providers
from subscription_models_v1_1 import ADDITIONAL_MODELS, register_models


class SubscriptionCatalogueTests(unittest.TestCase):
    @patch("providers.has_key", side_effect=lambda family: family == "codex-cli")
    def test_registration_preserves_frozen_suite_and_transport(self, has_key):
        before = suite_fingerprint()
        register_models()
        self.assertEqual(suite_fingerprint(), before)
        for slug, _ in ADDITIONAL_MODELS:
            provider = providers.get_provider(f"codex-cli/{slug}", reasoning_effort="low")
            self.assertIsInstance(provider, providers.CodexCLIProvider)
            self.assertEqual(provider.model, slug)
            self.assertEqual(provider.reasoning_effort, "low")
        self.assertEqual(has_key.call_count, len(ADDITIONAL_MODELS))

    def test_registration_does_not_duplicate_or_replace_existing_models(self):
        original = providers.model_info("codex-cli/gpt-6-astra")
        register_models()
        count = len(providers.MODELS)
        register_models()
        self.assertEqual(len(providers.MODELS), count)
        self.assertIs(providers.model_info("codex-cli/gpt-6-astra"), original)


if __name__ == "__main__":
    unittest.main()
