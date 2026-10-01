---
name: mager-bench
description: A pickup basketball court for coding models, with a model lineup and complete box scores.
colors:
  court: "oklch(13% 0.006 270)"
  raised: "oklch(18% 0.01 270)"
  chalk: "oklch(94% 0.009 265)"
  secondary: "oklch(71% 0.022 268)"
  green: "oklch(83% 0.185 153)"
  blue: "oklch(76% 0.14 249)"
  purple: "oklch(76% 0.15 305)"
  rule: "oklch(31% 0.017 270)"
typography:
  headlines: "Barlow Condensed, 700–800"
  body: "Manrope"
  data: "IBM Plex Mono"
---

## Direction

Near-black surfaces with green identity, blue original scores, and purple
Counterexample results. The model lineup is a dark, terminal-style scoreboard.
A geometric basketball mark and native SVG
court diagram make the pickup-game reference concrete. No stock imagery or
AI-generated bitmap is needed. Avoid simulated grime, gradients, glow, or motion
that suggests an actual live game.

## Hierarchy

The homepage begins with a compact court identity and the models. Model names,
the original coding score, and every Counterexample attempt share a clear row.
The next section compares both models across thirteen original challenges and
the new test, with skill filters and inline explanations. A concrete failed
transfer introduces the dedicated Counterexample walkthrough.

Model profiles contain both scoring histories. Historical raw answers remain
at their original routes, with the old scoring method labeled. The challenge
index explains both systems and all fourteen prompts/records.

## Typography

Barlow Condensed carries the wordmark and sports-style headings. Use uppercase
for short display text. Manrope carries prose, controls, and task names; IBM
Plex Mono carries small metadata, units, and exact values. UI controls and data
never use decorative display type. Keep explanation text under 75ch.

## Layout and interaction

1200px shell, 36px desktop gutters, 18px mobile gutters. Thin rules and flat
rows organize the evidence. Avoid repeated promotional cards. The lineup
is one shared scoreboard. On phones, each model
and each challenge becomes a stacked record with visible labels for every unit.

Skill filters use ordinary buttons with visible selection state. Inline native
disclosures explain each challenge without leaving the comparison. Every score
links to evidence. The Counterexample walkthrough retains scenario selection,
step selection, replay, and exact oracle-generated outputs.

## Accessibility

High-contrast type, visible focus, semantic comparison tables, text labels with
all color states, and reduced-motion support. Long code and trace tables can
scroll locally. The page itself must never overflow on a phone. Court graphics
are decorative and hidden from accessibility APIs.
