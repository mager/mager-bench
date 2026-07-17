# Product

## Register

product

## Users

Andrew ("Mager"), a solo developer who runs this bench himself every time a
new coding model drops, plus other developers who land on the public site
out of curiosity about how models stack up on tasks that actually resemble
day-to-day coding work. A third audience: people who want to *fund* a
head-to-head without running anything themselves — they care about the
leaderboard filling out, not about owning API keys.

Nobody is here to sign up or convert into a SaaS customer. They're here to
read scores, inspect *why* a model scored what it scored, and optionally
pitch in so the expensive models get a fair run.

## Product Purpose

mager-bench is a small, opinionated, personally-curated benchmark: twelve
coding tasks Mager actually cares about, run against any model, scored by
an LLM judge on correctness, code quality, and documentation.

**Free first.** Default subjects and judges are free-tier models (Groq Llama,
Gemini Flash). Cheap models (Haiku, GPT-4o mini) are optional pennies.
Paid models (Opus, GPT-4o, Sonnet flagships) sit on a public wishlist and
get unlocked via crowdfunding or BYO keys.

The web dashboard is the public face of that CLI tool — a multi-model
leaderboard plus a transparent paper trail (challenge prompt, rubric, and
the model's actual response) so a visitor can inspect *why* a score landed
where it did. The `/fund` page turns "I wish someone would run Opus" into
an actual gas tank for API tokens.

Success = a developer looks at this and immediately understands both the
ranking and the reasoning, feels a little competitive urge to see their
favorite model climb it, and (when it's a paid model) has a one-click path
to help pay for that climb.

## Brand Personality

Nerdy, playful, technically confident. CRT hacker-terminal energy — amber
phosphor glow, monospace type, a blinking cursor — but legible first,
retro-flavor second. Tone is "I built a scrappy benchmark in my basement
and it's weirdly rigorous," not "enterprise AI eval platform." Confident
and a little competitive: this should read like a benchmark models *want*
to pass, not a dry spreadsheet. Crowdfunding voice is the same energy —
"chip in for gas money," not charity guilt or startup pitch deck.

## Anti-references

- Generic SaaS eval dashboards: cream/gray cards, hero-metric-with-gradient-accent
  templates, tiny uppercase eyebrows over every section.
- Sterile MLPerf/HuggingFace-leaderboard-style plain tables with no
  personality and no way to see the actual model output behind a score.
- Corporate AI-benchmark marketing sites (polished, faceless, blue-gradient).
- Cute-but-illegible retro terminal skins where the aesthetic wins and the
  actual numbers/text become hard to read.
- Kickstarter-style crowdfunding theater (fake urgency, stretch-goal confetti).
  The fund page is a wishlist + gas tank, not a campaign.

## Design Principles

1. **Show your work.** Every score must trace back to the real prompt,
   rubric, and model response — no black-box numbers.
2. **Free first, fund the rest.** Default paths never require a credit card.
   Crowdfunding is optional fuel for paid seats, not a paywall on the bench.
3. **One consistent nerdy-terminal voice.** Amber CRT aesthetic, applied
   deliberately across every new surface (homepage, challenges, fund).
4. **Small and honest.** This is a personal bench, not an enterprise eval
   suite — lean into that self-aware, scrappy framing.
5. **Legible first, glow second.** Retro effects are additive polish; they
   must never reduce contrast or readability of the actual data.
6. **Measure variance.** Single runs are vibes; multi-run means ±σ are how
   you quote numbers.

## Accessibility & Inclusion

WCAG AA contrast minimum (4.5:1 body text, 3:1 large/bold text) even
against the dark amber theme. All CRT-style motion (flicker, blink, scan)
must respect `prefers-reduced-motion` with an instant/crossfade fallback.
