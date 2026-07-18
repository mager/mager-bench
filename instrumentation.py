"""Arize AX tracing setup — optional, activates only when ARIZE_* env vars are set.

Initialize before any LLM client is created (bench.py calls setup_tracing()
at the top of main). Groq rides the OpenAI instrumentor (same SDK); Gemini
uses the legacy google-generativeai SDK with no auto-instrumentor, so
providers.py emits a manual LLM span for it.
"""

from __future__ import annotations

import os

PROJECT_NAME = "mager-bench"

_tracer_provider = None


def setup_tracing():
    """Register the Arize OTLP exporter + instrumentors. Returns the tracer
    provider, or None when credentials are missing (bench runs untraced)."""
    global _tracer_provider
    if _tracer_provider is not None:
        return _tracer_provider

    api_key = os.environ.get("ARIZE_API_KEY")
    space_id = os.environ.get("ARIZE_SPACE_ID")
    if not api_key or not space_id:
        print("  tracing: ARIZE_API_KEY / ARIZE_SPACE_ID not set — skipping")
        return None

    from arize.otel import register
    from openinference.instrumentation.anthropic import AnthropicInstrumentor
    from openinference.instrumentation.openai import OpenAIInstrumentor

    _tracer_provider = register(
        space_id=space_id,
        api_key=api_key,
        project_name=PROJECT_NAME,
    )
    AnthropicInstrumentor().instrument(tracer_provider=_tracer_provider)
    OpenAIInstrumentor().instrument(tracer_provider=_tracer_provider)
    print(f"  tracing: Arize AX enabled (project={PROJECT_NAME})")
    return _tracer_provider


def get_tracer(name: str = PROJECT_NAME):
    from opentelemetry import trace
    return trace.get_tracer(name)


def flush_tracing() -> None:
    """CLI app: ship buffered spans before the process exits."""
    if _tracer_provider is not None:
        _tracer_provider.force_flush()
        _tracer_provider.shutdown()
