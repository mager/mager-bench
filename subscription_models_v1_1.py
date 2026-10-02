"""Add subscription subjects without editing the frozen v1.1 harness files.

Usage: python subscription_models_v1_1.py --model codex-cli/gpt-6.1-sol ...
All arguments are passed to bench_v1_1.main. Only catalogue metadata is added;
the provider implementation, prompt, budgets, runner, and scorer stay frozen.
"""

import providers


ADDITIONAL_MODELS = (
    ("gpt-6.1-sol", "GPT-6.1 Sol"),
    ("gpt-6-luna", "GPT-6 Luna"),
    ("gpt-5.6-terra", "GPT-5.6 Terra"),
    ("gpt-5.6-luna", "GPT-5.6 Luna"),
    ("gpt-5.5", "GPT-5.5"),
)


def register_models():
    for slug, name in ADDITIONAL_MODELS:
        identifier = f"codex-cli/{slug}"
        if providers.model_info(identifier) is not None:
            continue
        info = providers.ModelInfo(
            identifier, "codex-cli", slug, "subscription",
            f"{name} (Codex CLI)", "Additional v1.1 subscription subject",
        )
        providers.MODELS.append(info)
        providers._BY_ID[identifier] = info
        providers.AVAILABLE_MODELS.append(identifier)


if __name__ == "__main__":
    from bench_v1_1 import main

    register_models()
    raise SystemExit(main())
