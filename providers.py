"""Model provider adapters — one class per API.

Models are tagged free | cheap | paid so the CLI can default to wallet-friendly
runs. Free-tier keys (Groq, Gemini free) are enough for a full leaderboard;
paid models are the ones crowdfunding is meant to unlock.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

Tier = Literal["free", "cheap", "paid"]


@dataclass(frozen=True)
class ModelInfo:
    id: str
    family: str
    api_model: str
    tier: Tier
    display_name: str
    notes: str = ""


# Canonical catalogue. Order is the default run order (free first).
MODELS: list[ModelInfo] = [
    # ── free tier (no card / free quota) ──────────────────────────────────
    ModelInfo("llama-3.3-70b", "groq", "llama-3.3-70b-versatile", "free", "Llama 3.3 70B", "Groq free tier"),
    ModelInfo("llama-3.1-8b", "groq", "llama-3.1-8b-instant", "free", "Llama 3.1 8B", "Groq free tier — fast baseline"),
    # gemini-2.0-flash retired by Google (generateContent 404s as of 2026-07) — 2.5-flash is the free successor
    ModelInfo("gemini-2.5-flash", "gemini", "gemini-2.5-flash", "free", "Gemini 2.5 Flash", "Google AI Studio free tier"),
    # ── cheap (pennies per full bench) ────────────────────────────────────
    ModelInfo("claude-haiku-4-5", "anthropic", "claude-haiku-4-5", "cheap", "Claude Haiku 4.5", "cheap Anthropic default"),
    ModelInfo("gpt-4o-mini", "openai", "gpt-4o-mini", "cheap", "GPT-4o mini"),
    # ── paid (real money — fund these via /fund) ──────────────────────────
    ModelInfo("claude-sonnet-4-6", "anthropic", "claude-sonnet-4-6", "paid", "Claude Sonnet 4.6"),
    ModelInfo("claude-sonnet-5", "anthropic", "claude-sonnet-5", "paid", "Claude Sonnet 5"),
    ModelInfo("claude-opus-4-8", "anthropic", "claude-opus-4-8", "paid", "Claude Opus 4.8"),
    ModelInfo("gpt-4o", "openai", "gpt-4o", "paid", "GPT-4o"),
    ModelInfo("gemini-2.5-pro", "gemini", "gemini-2.5-pro", "paid", "Gemini 2.5 Pro"),
]

_BY_ID = {m.id: m for m in MODELS}
AVAILABLE_MODELS = [m.id for m in MODELS]
FREE_MODELS = [m.id for m in MODELS if m.tier == "free"]
CHEAP_MODELS = [m.id for m in MODELS if m.tier in ("free", "cheap")]
PAID_MODELS = [m.id for m in MODELS if m.tier == "paid"]

# Judges that work without spending money. Prefer free first.
FREE_JUDGE_CANDIDATES = [
    "gemini-2.5-flash",
    "llama-3.3-70b",
    "claude-haiku-4-5",
]

_KEY_MAP = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
}


class Provider(ABC):
    @abstractmethod
    def complete(self, prompt: str, max_tokens: int = 2048) -> str: ...


class AnthropicProvider(Provider):
    def __init__(self, model: str) -> None:
        import anthropic
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.model = model

    def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        # Sonnet 5+ think by default and max_tokens caps thinking + text combined,
        # so a response can contain thinking blocks with no text block at all.
        text = "".join(
            block.text for block in msg.content
            if getattr(block, "type", None) == "text"
        )
        if not text:
            raise RuntimeError(
                f"{self.model}: no text in response "
                f"(stop_reason={msg.stop_reason}) — raise max_tokens"
            )
        return text


class OpenAIProvider(Provider):
    def __init__(self, model: str) -> None:
        from openai import OpenAI
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.model = model

    def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or ""


class GroqProvider(Provider):
    """Groq exposes an OpenAI-compatible API, so reuse the OpenAI SDK."""

    def __init__(self, model: str) -> None:
        from openai import OpenAI
        self.client = OpenAI(
            api_key=os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = model

    def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or ""


class GeminiProvider(Provider):
    def __init__(self, model: str) -> None:
        import google.generativeai as genai
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model_obj = genai.GenerativeModel(model)
        self.model_name = model

    def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        from instrumentation import get_tracer

        # Manual LLM span — the legacy google-generativeai SDK has no
        # openinference auto-instrumentor. No-op when tracing is off.
        with get_tracer().start_as_current_span("gemini.generate_content") as span:
            span.set_attribute("openinference.span.kind", "LLM")
            span.set_attribute("llm.model_name", self.model_name)
            span.set_attribute("input.value", prompt)
            # Gemini 2.5 models think by default and thoughts count against
            # max_output_tokens (legacy SDK has no thinking_config), so give
            # headroom or the visible answer gets truncated to a stub.
            resp = self.model_obj.generate_content(
                prompt,
                generation_config={"max_output_tokens": max_tokens + 8192},
            )
            span.set_attribute("output.value", resp.text)
            return resp.text


def model_info(model_id: str) -> ModelInfo | None:
    return _BY_ID.get(model_id)


def display_name(model_id: str) -> str:
    info = _BY_ID.get(model_id)
    return info.display_name if info else model_id


def has_key(family: str) -> bool:
    env_key = _KEY_MAP.get(family)
    return bool(env_key and os.environ.get(env_key))


def is_configured(model_id: str) -> bool:
    info = _BY_ID.get(model_id)
    if not info:
        return False
    return has_key(info.family)


def configured_models(tier: Tier | Literal["all", "free", "cheap"] = "all") -> list[str]:
    """Return model IDs that have an API key and match the tier filter."""
    out: list[str] = []
    for m in MODELS:
        if not has_key(m.family):
            continue
        if tier == "all":
            out.append(m.id)
        elif tier == "free" and m.tier == "free":
            out.append(m.id)
        elif tier == "cheap" and m.tier in ("free", "cheap"):
            out.append(m.id)
        elif tier in ("free", "cheap", "paid") and m.tier == tier:
            out.append(m.id)
    return out


def pick_default_judge() -> str:
    """Prefer a free/cheap configured judge so full runs stay free by default."""
    for candidate in FREE_JUDGE_CANDIDATES:
        if is_configured(candidate):
            return candidate
    # last resort: any configured model
    for m in MODELS:
        if has_key(m.family):
            return m.id
    return "gemini-2.5-flash"


def get_provider(model_id: str) -> Provider | None:
    info = _BY_ID.get(model_id)
    if not info:
        print(f"Unknown model: {model_id}")
        return None
    if not has_key(info.family):
        return None
    if info.family == "anthropic":
        return AnthropicProvider(info.api_model)
    if info.family == "openai":
        return OpenAIProvider(info.api_model)
    if info.family == "groq":
        return GroqProvider(info.api_model)
    if info.family == "gemini":
        return GeminiProvider(info.api_model)
    return None


def list_models_report() -> str:
    lines = ["id                           tier   key   display"]
    lines.append("─" * 64)
    for m in MODELS:
        key = "yes" if has_key(m.family) else "no"
        lines.append(f"{m.id:<28} {m.tier:<6} {key:<5} {m.display_name}")
    free = configured_models("free")
    cheap = configured_models("cheap")
    lines.append("")
    lines.append(f"configured free:  {', '.join(free) or '(none — set GROQ_API_KEY / GEMINI_API_KEY)'}")
    lines.append(f"configured cheap: {', '.join(cheap) or '(none)'}")
    lines.append(f"default judge:    {pick_default_judge()}")
    return "\n".join(lines)
