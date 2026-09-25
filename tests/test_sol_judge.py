import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from challenges import load_challenges
from judge import score_response
from providers import get_provider, pick_default_judge


VERDICT = '{"correctness":8,"quality":7,"documentation":6,"notes":"Test verdict"}'


def completion(text=VERDICT):
    return SimpleNamespace(choices=[SimpleNamespace(
        message=SimpleNamespace(content=text), finish_reason="stop")])


class SolJudgeTests(unittest.TestCase):
    def test_default_does_not_silently_change_with_credentials(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test"}, clear=True):
            self.assertEqual(pick_default_judge(), "codex-cli/gpt-5.6-sol")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test"}, clear=True)
    @patch("openai.OpenAI")
    def test_direct_judge_request_and_verdict(self, sdk):
        create = sdk.return_value.chat.completions.create
        create.return_value = completion()
        result = score_response(load_challenges(["fizzbuzz"])[0], "answer", "subject",
                                judge_model="gpt-6-sol",
                                max_tokens=4096)
        request = create.call_args.kwargs
        self.assertEqual(request["model"], "gpt-6-sol")
        self.assertEqual(request["max_completion_tokens"], 4096)
        self.assertEqual(request["reasoning_effort"], "low")
        self.assertNotIn("max_tokens", request)
        self.assertEqual(result["judge"], "gpt-6-sol")
        self.assertEqual(result["correctness"], 8)

    @patch.dict(os.environ, {"AI_GATEWAY_API_KEY": "test"}, clear=True)
    @patch("openai.OpenAI")
    def test_gateway_judge_does_not_add_subject_headroom(self, sdk):
        stream = MagicMock()
        stream.__iter__.return_value = iter([
            SimpleNamespace(type="content.delta", delta=VERDICT)])
        stream.get_final_completion.return_value = completion()
        call = sdk.return_value.chat.completions.stream
        call.return_value.__enter__.return_value = stream
        result = score_response(load_challenges(["fizzbuzz"])[0], "answer", "subject",
                                judge_model="gpt-6-sol",
                                max_tokens=4096)
        request = call.call_args.kwargs
        self.assertEqual(request["model"], "openai/gpt-6-sol")
        self.assertEqual(request["max_completion_tokens"], 4096)
        self.assertEqual(request["extra_body"]["reasoning_effort"], "low")
        self.assertNotIn("max_tokens", request)
        self.assertEqual(result["quality"], 7)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test"}, clear=True)
    @patch("openai.OpenAI")
    def test_legacy_openai_request_stays_compatible(self, sdk):
        create = sdk.return_value.chat.completions.create
        create.return_value = completion("OK")
        self.assertEqual(get_provider("gpt-4o-mini").complete("Say OK", 100), "OK")
        request = create.call_args.kwargs
        self.assertEqual(request["max_tokens"], 100)
        self.assertNotIn("max_completion_tokens", request)
        self.assertNotIn("reasoning_effort", request)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test"}, clear=True)
    @patch("openai.OpenAI")
    def test_empty_completion_is_an_error(self, sdk):
        sdk.return_value.chat.completions.create.return_value = completion("")
        with self.assertRaisesRegex(RuntimeError, "empty response"):
            get_provider("gpt-6-sol").complete("Say OK")


if __name__ == "__main__":
    unittest.main()
