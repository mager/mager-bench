"""
Model provider adapters — one class per API.

Models are tagged free | cheap | paid so the CLI can default to wallet-friendly
runs. Free-tier keys (Groq, Gemini free) are enough for a full leaderboard;
paid models are the ones crowdfunding is meant to unlock.

A single Vercel AI Gateway key (AI_GATEWAY_API_KEY) can stand in for every
per-provider key: families without their own key route through the gateway's
OpenAI-compatible endpoint with creator-prefixed model ids (zai/glm-5.3,
anthropic/claude-sonnet-5, …) and unified billing.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

Tier = Literal["free", "cheap", "paid"]

# Vercel AI Gateway — one OpenAI-compatible endpoint for every family.
GATEWAY_KEY = "AI_GATEWAY_API_KEY"
GATEWAY_BASE_URL = "https://ai-gateway.vercel.sh/v1"
# creator/ prefix the gateway expects, per family
_GATEWAY_CREATOR = {
    "anthropic": "anthropic/",
    "openai": "openai/",
    "gemini": "google/",
    "groq": "groq/",
    "zai": "zai/",
}


@dataclass(frozen=True)
class ModelInfo:
    id: str
    family: str
    api_model: str
    tier: Tier
    display_name: str
    notes: str = ""
    # Reasoning models spend tokens thinking before they answer, and most APIs
    # count those against the same budget as the answer. Flagged models get
    # extra headroom so their *visible* answer budget matches everyone else's.
    reasoning: bool = False
    # Free-tier tokens-per-minute ceiling, where the provider reserves
    # prompt + max_tokens against it up front (Groq does). Requests over the
    # ceiling are rejected outright (413), not throttled, so the harness has
    # to clamp rather than retry. None = no meaningful ceiling.
    tpm_ceiling: int | None = None


# Canonical catalogue. Order is the default run order (free first).
MODELS: list[ModelInfo] = [
    # ── free tier (no card / free quota) ──────────────────────────────────
    ModelInfo("llama-3.3-70b", "groq", "llama-3.3-70b-versatile", "free", "Llama 3.3 70B", "Groq free tier",
              tpm_ceiling=12000),
    ModelInfo("llama-3.1-8b", "groq", "llama-3.1-8b-instant", "free", "Llama 3.1 8B", "Groq free tier — fast baseline",
              tpm_ceiling=6000),
    ModelInfo("gpt-oss-120b", "groq", "openai/gpt-oss-120b", "free", "GPT-OSS 120B",
              "OpenAI open-weights, served on Groq free tier", reasoning=True, tpm_ceiling=8000),
    # gemini-2.0-flash retired by Google (generateContent 404s as of 2026-07) — 2.5-flash is the free successor
    ModelInfo("gemini-2.5-flash", "gemini", "gemini-2.5-flash", "free", "Gemini 2.5 Flash", "Google AI Studio free tier"),
    # ── cheap (pennies per full bench) ────────────────────────────────────
    ModelInfo("claude-haiku-4-5", "anthropic", "claude-haiku-4-5", "cheap", "Claude Haiku 4.5", "cheap Anthropic default"),
    ModelInfo("gpt-4o-mini", "openai", "gpt-4o-mini", "cheap", "GPT-4o mini"),
    # gateway promo (no direct-API equivalent — cheap + heavily prompt-cached)
    ModelInfo("glm-5.3-promo", "gateway", "zai/glm-5.3-promo-50", "cheap", "GLM 5.3 Promo",
              "AI Gateway promo pricing + heavy caching — best for big-context reruns"),
    # ── paid (real money — fund these via /fund) ──────────────────────────
    ModelInfo("claude-sonnet-4-6", "anthropic", "claude-sonnet-4-6", "paid", "Claude Sonnet 4.6"),
    ModelInfo("claude-sonnet-5", "anthropic", "claude-sonnet-5", "paid", "Claude Sonnet 5"),
    ModelInfo("claude-opus-4-8", "anthropic", "claude-opus-4-8", "paid", "Claude Opus 4.8"),
    ModelInfo("gpt-4o", "openai", "gpt-4o", "paid", "GPT-4o"),
    ModelInfo("gemini-2.5-pro", "gemini", "gemini-2.5-pro", "paid", "Gemini 2.5 Pro"),
    # GLM 5.3 (2026-08): reasoning cannot be disabled — thinking is billed and
    # counts against max_tokens, so it runs at high effort with thinking headroom
    ModelInfo("glm-5.3", "zai", "glm-5.3", "paid", "GLM 5.3",
              "Zhipu Z.ai flagship coder — reasoning always on", reasoning=True),
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
    "zai": "ZAI_API_KEY",
    "gateway": "AI_GATEWAY_API_KEY",
}


class Provider(ABC):
    @abstractmethod
    def complete(self, prompt: str, max_tokens: int = 2048) -> str: ...


class AnthropicProvider(Provider):
    # Sonnet 5+ thinks by default with an uncapped budget: live gateway logs
    # showed 5–8k reasoning tokens per judge call ($0.05–0.08 a pop, 55–83s).
    # thinking_budget caps it; None = leave the model to its own devices.
    def __init__(self, model: str, thinking_budget: int | None = None) -> None:
        import anthropic
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.model = model
        self.thinking_budget = thinking_budget

    def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        kwargs: dict = {}
        if self.thinking_budget:
            # budget must sit under max_tokens or the API rejects the call
            max_tokens = max(max_tokens, self.thinking_budget + 1024)
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": self.thinking_budget}
        try:
            msg = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
        except Exception:
            if not kwargs:
                raise
            # older / non-thinking models reject the thinking param — retry plain
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

    def __init__(self, model: str, reasoning: bool = False, tpm_ceiling: int | None = None) -> None:
        from openai import OpenAI
        self.client = OpenAI(
            api_key=os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1",
            # Free tier is tokens-per-minute limited; let the SDK sit out the
            # 429s (it honours retry-after) instead of failing the challenge.
            max_retries=6,
        )
        self.model = model
        self.reasoning = reasoning
        self.tpm_ceiling = tpm_ceiling

    def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        kwargs = {}
        if self.reasoning:
            # Groq bills reasoning tokens against max_tokens, so without headroom
            # a thinking model's answer gets truncated mid-implementation.
            # "parsed" keeps the chain-of-thought out of message.content — it's a
            # Groq-only param, so it rides in extra_body (the OpenAI SDK rejects
            # unknown top-level kwargs).
            max_tokens += 2048
            kwargs["extra_body"] = {"reasoning_format": "parsed"}
        if self.tpm_ceiling:
            # Groq reserves prompt + max_tokens against the per-minute ceiling
            # and rejects (413) rather than throttles, so clamp to what fits.
            # ~4 chars/token, plus a margin for the tokenizer estimate.
            budget = self.tpm_ceiling - (len(prompt) // 4) - 256
            max_tokens = max(256, min(max_tokens, budget))
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        text = resp.choices[0].message.content or ""
        if not text:
            raise RuntimeError(
                f"{self.model}: empty response "
                f"(finish_reason={resp.choices[0].finish_reason}) — raise max_tokens"
            )
        return text


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


class ZaiProvider(Provider):
    """Z.ai (Zhipu) direct — OpenAI-compatible chat API.

    GLM 5.3 cannot run with thinking disabled — reasoning tokens are billed
    and count against max_tokens — so flagged models get generous headroom
    and run at high effort so their *visible* answer budget matches everyone
    else's. `reasoning_content` stays out of message.content, so the answer
    text arrives clean.
    """

    THINKING_HEADROOM = 32768

    def __init__(self, model: str, reasoning: bool = False) -> None:
        from openai import OpenAI
        # GLM Coding Plan keys must use the coding endpoint instead —
        # override with ZAI_BASE_URL in .env.
        base_url = os.environ.get("ZAI_BASE_URL", "https://api.z.ai/api/paas/v4")
        self.client = OpenAI(
            api_key=os.environ["ZAI_API_KEY"],
            base_url=base_url,
            max_retries=6,
        )
        self.model = model
        self.reasoning = reasoning

    def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        kwargs = {}
        if self.reasoning:
            max_tokens += self.THINKING_HEADROOM
            # Z.ai-only params ride in extra_body (the OpenAI SDK rejects
            # unknown top-level kwargs).
            kwargs["extra_body"] = {
                "thinking": {"type": "enabled"},
                "reasoning_effort": "high",
            }
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        text = resp.choices[0].message.content or ""
        if not text:
            raise RuntimeError(
                f"{self.model}: empty response "
                f"(finish_reason={resp.choices[0].finish_reason}) — raise max_tokens"
            )
        return text


class GatewayProvider(Provider):
    """Vercel AI Gateway — one OpenAI-compatible endpoint for every family.

    Serves any creator/model id on the gateway (zai/glm-5.3,
    anthropic/claude-sonnet-5, google/gemini-2.5-flash, …) with unified
    billing, so a single AI_GATEWAY_API_KEY can run subjects and judges
    without per-provider keys. Used only when a family's own key is absent.

    Streams + accumulates: same return contract as blocking, but long calls
    stay observable (stderr heartbeat every 30s) and a mid-stream cut reports
    how far it got instead of vanishing silently. Thinking models are quiet
    during the think phase regardless — the heartbeat is liveness, not a
    progress bar. Live 2026-09-04: GLM 5.3 burned 15k thinking tokens before
    writing a char on doom/slots, so reasoning models get 32768 headroom
    (billed only on actual use).
    """

    def __init__(self, model: str, reasoning: bool = False,
                 reasoning_effort: str | None = None,
                 thinking_headroom: int = 32768,
                 timeout: float = 1800) -> None:
        from openai import OpenAI
        self.client = OpenAI(
            api_key=os.environ[GATEWAY_KEY],
            base_url=GATEWAY_BASE_URL,
            max_retries=6,
            # big-build calls run 5–10+ min; the SDK's 10-min default
            # decapitates them mid-generation
            timeout=timeout,
        )
        self.model = model
        self.reasoning = reasoning
        self.reasoning_effort = reasoning_effort or ("high" if reasoning else None)
        self.thinking_headroom = thinking_headroom if reasoning else 0

    def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        import sys
        import time

        kwargs: dict = {}
        max_tokens += self.thinking_headroom
        if self.reasoning_effort:
            # provider-agnostic effort; the gateway maps it onto each
            # model's native config. Override per-run via --reasoning-effort.
            kwargs["extra_body"] = {"reasoning_effort": self.reasoning_effort}

        t0 = time.monotonic()
        last_beat = t0
        parts: list[str] = []
        think_chars = 0
        try:
            with self.client.chat.completions.stream(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            ) as stream:
                for event in stream:
                    if event.type == "content.delta":
                        # the SDK fans raw chunks out into typed events;
                        # text arrives here with delta as a plain str
                        parts.append(event.delta)
                    elif event.type == "chunk":
                        # providers that expose the think stream put it on
                        # the raw chunk's delta (SDK- and provider-dependent;
                        # absent → think_chars just stays 0)
                        try:
                            choices = event.chunk.choices or []
                            d = choices[0].delta if choices else None
                            think = getattr(d, "reasoning_content", None) or ""
                            think_chars += len(think) if isinstance(think, str) else 0
                        except Exception:
                            pass
                    now = time.monotonic()
                    if now - last_beat >= 30:
                        el = int(now - t0)
                        print(f"  [gateway {self.model} +{el}s: "
                              f"{sum(map(len, parts))} text chars, "
                              f"{think_chars} think chars]",
                              file=sys.stderr, flush=True)
                        last_beat = now
                final = stream.get_final_completion()
        except Exception as e:
            salvaged = sum(map(len, parts))
            raise RuntimeError(
                f"{self.model} via AI Gateway: stream cut after "
                f"{int(time.monotonic() - t0)}s "
                f"({salvaged} text chars, {think_chars} think chars salvaged): {e}"
            )
        text = "".join(parts) or (
            (final.choices[0].message.content or "") if final.choices else ""
        )
        if not text:
            finish = (final.choices[0].finish_reason
                      if final.choices else "unknown")
            raise RuntimeError(
                f"{self.model} via AI Gateway: empty response "
                f"(finish_reason={finish}) — raise max_tokens or thinking_headroom"
            )
        return text
def model_info(model_id: str) -> ModelInfo | None:
    return _BY_ID.get(model_id)


def display_name(model_id: str) -> str:
    info = _BY_ID.get(model_id)
    return info.display_name if info else model_id


def has_key(family: str) -> bool:
    # a gateway key stands in for any missing family key
    if os.environ.get(GATEWAY_KEY):
        return True
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


def get_provider(model_id: str, thinking_budget: int | None = None,
                 reasoning_effort: str | None = None,
                 thinking_headroom: int = 32768,
                 gateway_timeout: float = 1800) -> Provider | None:
    info = _BY_ID.get(model_id)
    if not info:
        print(f"Unknown model: {model_id}")
        return None
    if not has_key(info.family):
        return None
    # direct family key wins; otherwise route through the Vercel AI Gateway
    if not os.environ.get(_KEY_MAP.get(info.family, "")):
        if os.environ.get(GATEWAY_KEY):
            return GatewayProvider(
                _GATEWAY_CREATOR.get(info.family, "") + info.api_model,
                reasoning=info.reasoning,
                reasoning_effort=reasoning_effort,
                thinking_headroom=thinking_headroom,
                timeout=gateway_timeout,
            )
        return None
    if info.family == "anthropic":
        return AnthropicProvider(info.api_model, thinking_budget=thinking_budget)
    if info.family == "openai":
        return OpenAIProvider(info.api_model)
    if info.family == "groq":
        return GroqProvider(info.api_model, reasoning=info.reasoning, tpm_ceiling=info.tpm_ceiling)
    if info.family == "gemini":
        return GeminiProvider(info.api_model)
    if info.family == "zai":
        return ZaiProvider(info.api_model, reasoning=info.reasoning)
    if info.family == "gateway":
        return GatewayProvider(info.api_model,
                               reasoning=info.reasoning,
                               reasoning_effort=reasoning_effort,
                               thinking_headroom=thinking_headroom,
                               timeout=gateway_timeout)
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
