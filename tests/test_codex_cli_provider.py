import os
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from providers import CodexCLIProvider
from challenges import load_challenges
from judge import score_response


class CodexCLIProviderTests(unittest.TestCase):
    @patch.dict(os.environ, {"OPENAI_API_KEY": "api-key", "CODEX_ACCESS_TOKEN": "token"})
    @patch("providers.subprocess.run")
    def test_uses_chatgpt_login_and_returns_only_final_message(self, run):
        def fake_run(args, **kwargs):
            Path(args[args.index("--output-last-message") + 1]).write_text("Answer\n")
            self.assertNotIn("OPENAI_API_KEY", kwargs["env"])
            self.assertNotIn("CODEX_ACCESS_TOKEN", kwargs["env"])
            self.assertIn("--ephemeral", args)
            self.assertIn("read-only", args)
            self.assertIn("gpt-5.6-sol", args)
            self.assertIn("Write fizzbuzz", kwargs["input"])
            return CompletedProcess(args, 0, "", "")

        run.side_effect = fake_run
        answer = CodexCLIProvider("gpt-5.6-sol").complete("Write fizzbuzz", 500)
        self.assertEqual(answer, "Answer")

    @patch("providers.subprocess.run")
    def test_failed_cli_session_is_not_a_score(self, run):
        run.return_value = CompletedProcess(["codex"], 1, "", "ERROR: unavailable")
        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            CodexCLIProvider("gpt-5.6-sol").complete("Write fizzbuzz")

    @patch("judge.get_provider")
    def test_cli_judge_sees_full_large_response(self, get_provider):
        get_provider.return_value.complete.return_value = (
            '{"correctness": 8, "quality": 8, "documentation": 8, "notes": "complete"}'
        )
        response = "a" * 6000 + "END_OF_RESPONSE"
        score_response(load_challenges(["doom"])[0], response, "subject",
                       judge_model="codex-cli/gpt-5.6-sol")
        prompt = get_provider.return_value.complete.call_args.args[0]
        self.assertIn("END_OF_RESPONSE", prompt)


if __name__ == "__main__":
    unittest.main()
