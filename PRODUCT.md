# Product

## Register

product

## Users

Andrew ("Mager"), a solo developer who runs this bench himself every time a
new coding model drops, plus other developers who land on the public site
out of curiosity about how models stack up on tasks that actually resemble
day-to-day coding work. Nobody is here to sign up or convert — they're here
to read scores and, ideally, click into *why* a model scored what it scored.

## Product Purpose

mager-bench is a small, opinionated, personally-curated benchmark: a dozen
coding tasks Mager actually cares about (from FizzBuzz to a single-file Doom
raycaster), run against any model, scored by
an LLM judge on correctness, code quality, and documentation. The web
dashboard is the public face of that CLI tool — a leaderboard plus, crucially,
a transparent paper trail (challenge prompt, rubric, and the model's actual
response) so a visitor can inspect *why* a score landed where it did, not
just trust a number. Success = a developer looks at this and immediately
understands both the ranking and the reasoning, and maybe feels a little
competitive urge to see their favorite model climb it.

## Brand Personality

Nerdy, playful, technically confident. CRT hacker-terminal energy — amber
phosphor glow, monospace type, a blinking cursor — but legible first,
retro-flavor second (glow/scanlines are seasoning, not camouflage for the
actual data). Tone is "I built a scrappy benchmark in my basement and it's
weirdly rigorous," not "enterprise AI eval platform." Confident and a
little competitive: this should read like a benchmark models *want* to
pass, not a dry spreadsheet.

## Anti-references

- Generic SaaS eval dashboards: cream/gray cards, hero-metric-with-gradient-accent
  templates, tiny uppercase eyebrows over every section.
- Sterile MLPerf/HuggingFace-leaderboard-style plain tables with no
  personality and no way to see the actual model output behind a score.
- Corporate AI-benchmark marketing sites (polished, faceless, blue-gradient).
- Cute-but-illegible retro terminal skins where the aesthetic wins and the
  actual numbers/text become hard to read (already corrected once on this
  project — glow effects must never drop body text below readable contrast).

## Design Principles

1. **Show your work.** Every score must trace back to the real prompt,
   rubric, and model response — no black-box numbers.
2. **One consistent nerdy-terminal voice.** Amber CRT aesthetic, applied
   deliberately across every new surface (not just the homepage).
3. **Small and honest.** This is a small personal bench, not an enterprise
   eval suite — lean into that self-aware, scrappy framing rather than
   inflating it with corporate polish.
4. **Legible first, glow second.** Retro effects (scanlines, flicker, text
   glow) are additive polish; they must never reduce contrast or readability
   of the actual data.

## Accessibility & Inclusion

WCAG AA contrast minimum (4.5:1 body text, 3:1 large/bold text) even
against the dark amber theme. All CRT-style motion (flicker, blink, scan)
must respect `prefers-reduced-motion` with an instant/crossfade fallback.
