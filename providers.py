"""Model provider adapters — one class per API."""

import os
from abc import ABC, abstractmethod

# Models available if the right API key is set
AVAILABLE_MODELS = [
    "claude-opus-4-8",
    "claude-sonnet-4-6",
    "gpt-4o",
    "gpt-4o-mini",
    "gemini-2.0-flash",
    "gemini-2.5-pro",
]


class Provider(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str: ...


class AnthropicProvider(Provider):
    def __init__(self, model: str) -> None:
        import anthropic
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.model = model

    def complete(self, prompt: str) -> str:
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text


class OpenAIProvider(Provider):
    def __init__(self, model: str) -> None:
        from openai import OpenAI
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.model = model

    def complete(self, prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or ""


class GeminiProvider(Provider):
    def __init__(self, model: str) -> None:
        import google.generativeai as genai
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model_obj = genai.GenerativeModel(model)

    def complete(self, prompt: str) -> str:
        resp = self.model_obj.generate_content(prompt)
        return resp.text


_MODEL_MAP = {
    "claude-opus-4-8": ("anthropic", "claude-opus-4-8"),
    "claude-sonnet-4-6": ("anthropic", "claude-sonnet-4-6"),
    "gpt-4o": ("openai", "gpt-4o"),
    "gpt-4o-mini": ("openai", "gpt-4o-mini"),
    "gemini-2.0-flash": ("gemini", "gemini-2.0-flash"),
    "gemini-2.5-pro": ("gemini", "gemini-2.5-pro"),
}

_KEY_MAP = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


def get_provider(model_id: str) -> Provider | None:
    if model_id not in _MODEL_MAP:
        print(f"Unknown model: {model_id}")
        return None
    family, model_name = _MODEL_MAP[model_id]
    env_key = _KEY_MAP[family]
    if not os.environ.get(env_key):
        return None
    if family == "anthropic":
        return AnthropicProvider(model_name)
    if family == "openai":
        return OpenAIProvider(model_name)
    if family == "gemini":
        return GeminiProvider(model_name)
    return None
