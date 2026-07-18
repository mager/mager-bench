---
name: mager-bench
description: CRT amber terminal dashboard for a personal coding-model benchmark, with ANSI-inspired accent colors per rubric dimension
colors:
  bg: "#000000"
  bg-raised: "#100a03"
  fg: "#e8e1cf"
  fg-dim: "#a79c86"
  amber: "#ffb000"
  amber-bright: "#ffd479"
  amber-dim: "#a4790f"
  amber-faint: "#57400a"
  alert: "#ff4433"
  green: "oklch(78% 0.17 152)"
  green-dim: "oklch(55% 0.12 152)"
  magenta: "oklch(74% 0.20 335)"
  magenta-dim: "oklch(52% 0.14 335)"
  cyan: "oklch(78% 0.13 220)"
  cyan-dim: "oklch(55% 0.10 220)"
typography:
  display:
    fontFamily: "VT323, monospace"
    fontSize: "clamp(2.5rem, 9vw, 9rem)"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: "0.02em"
  body:
    fontFamily: "IBM Plex Mono, monospace"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
spacing:
  sm: "8px"
  md: "16px"
  lg: "24px"
components:
  card:
    backgroundColor: "{colors.bg-raised}"
    textColor: "{colors.amber}"
    padding: "16px"
  card-hover:
    backgroundColor: "{colors.bg-raised}"
    textColor: "{colors.amber}"
  leaderboard-row:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.amber}"
  score-green:
    textColor: "{colors.green}"
  score-yellow:
    textColor: "{colors.amber}"
  score-red:
    textColor: "{colors.alert}"
---

## Overview

mager-bench is a CRT hacker-terminal dashboard for a personal coding-model
benchmark: amber phosphor glow on near-black, scanlines and vignette, a
blinking block cursor, VT323 for big display numbers and IBM Plex Mono for
everything meant to be read closely. The mood is "scrappy but rigorous" —
retro terminal energy in service of a real, inspectable eval, not decoration
for its own sake. Legibility always wins over atmosphere: glow and scanlines
are seasoning on top of body text that must clear WCAG AA on its own.

Anti-references: generic SaaS eval-dashboard cream/gray cards, sterile
MLPerf/HuggingFace-leaderboard tables, corporate AI-benchmark marketing
sites, and — importantly — a *too-committed* retro skin where the aesthetic
wins and scores become hard to read (two separate legibility passes have
corrected exactly that failure mode: capping VT323 to headline sizes, and
later moving default body copy off saturated amber onto `--fg`; see Do's
and Don'ts).

## Colors

**`--fg` / `--fg-dim`** are the default readable text colors — body copy,
descriptions, prompts, rubric text, labels, meta chrome. Amber is visually
loud enough that at body-copy sizes, under the scanline/glow effects, it
reads as fatiguing even when it numerically clears WCAG AA. `--fg` is used
for anything meant to be read closely; `--fg-dim` for secondary/meta text
(timestamps, section labels, table chrome).

**Amber** (`--amber` / `--amber-bright` / `--amber-dim` / `--amber-faint`)
is reserved for brand and interactive elements now, not default body text:
headings, links/hover states, the "yellow" score tier, and terminal-chrome
glyphs (`$`, `#`, dotted rules).

Three ANSI-terminal-inspired accents give each rubric dimension its own
identity wherever scores are broken down: **green** = correctness, **magenta**
= quality, **cyan** = documentation. All three are held at the same
lightness/chroma as each other (only hue changes) so they read as a
deliberate coded system, not random color. They appear as small dots +
bold values next to metric labels — categorical encoding, not a severity
signal.

Separately, every score/rating in the app — including the hero average —
uses a three-band traffic-light tier: **green** for scores over 9.5,
**amber/"yellow"** for 7–9.5, **red/alert** for anything below 7. This is a
different color *system* from the dimension accents above (severity vs.
category) and only appears on aggregate/total numbers, never on the
per-dimension values, so the two systems don't collide visually.

`--alert` (red) is reserved for sub-7 scores only — never decorative.

## Typography

Two families on a serif-adjacent contrast axis for a terminal, not a
humanist-vs-geometric pairing: **VT323** (pixel/CRT display face) for the
hero score and page/section titles — large, glowing, decorative-but-load-bearing.
**IBM Plex Mono** for everything else: body copy, labels, values, prompts,
rubric text. VT323 is capped to headline/hero use only; it was previously
used at body-copy sizes on challenge-breakdown cards and read poorly, so it
never appears below ~24px.

## Elevation

Flat, tonal system — no shadows. Depth comes from two surface levels:
`--bg` (page) and `--bg-raised` (cards, at ~40% opacity over the page
gradient) plus `--amber-faint` hairline borders. Glow (`text-shadow`) stands
in for elevation on interactive/important text instead of box-shadow.

## Components

- **Card** (`border border-amber-faint bg-bg-raised/40`): the base container
  for leaderboard rows expressed as cards, challenge breakdowns, rubric
  tiles, and challenge-definition result cards. Hairline border only —
  never a side-stripe accent.
- **`.lift`**: hover treatment for interactive cards/rows — 2px translateY,
  border brightens to `amber-dim`, background warms very slightly toward
  amber. Respects `prefers-reduced-motion` (color change only, no transform).
- **Dimension dot**: a 1.5×1.5 rounded dot in green/magenta/cyan preceding
  a metric label — the categorical color-coding unit, reused identically on
  the homepage breakdown and every challenge-definition results card.
- **Terminal window chrome**: three dots (red/amber/green, at 70% opacity)
  atop the prompt `<pre>` block on challenge pages, mimicking a terminal
  titlebar — the one place decorative color is allowed to be purely
  atmospheric, since it doesn't compete with data.
- **Glow classes**: `.glow` (amber), `.glow-alert` (red), `.glow-green`,
  `.glow-magenta`, `.glow-cyan` — paired 1:1 with the matching `text-*`
  color, always on already-colored text, never added on its own for
  decoration. The hero average uses the same tier glow as every other
  score display (no separate "hero-only" glow variant), so its color and
  intensity shift with the tier system instead of staying fixed amber.

## Do's and Don'ts

**Do**
- Keep VT323 to headline sizes only; body/metric text stays in IBM Plex Mono.
- Default body copy, descriptions, and prompt/rubric text to `--fg` (or
  `--fg-dim` for secondary/meta text) — not amber. Amber is for brand,
  interactive, and tier-colored elements only, so it stays legible instead
  of fatiguing at reading sizes.
- Use green/magenta/cyan only as the correctness/quality/documentation
  identity — don't introduce a fourth categorical hue without a fourth
  category to justify it.
- Apply the green/amber(yellow)/red tier system to every score/rating
  shown, including the hero average — not just the per-challenge totals —
  so a score's color always means the same thing everywhere it appears:
  green >9.5, amber/yellow 7–9.5, red <7.
- Respect `prefers-reduced-motion` on every animation (flicker, rise,
  cursor blink, lift) — instant/no-transform fallback, not just "less."

**Don't**
- Don't use `border-left`/`border-right` as a colored accent stripe on
  cards or callouts (an earlier version of the notes block did this — fixed
  to a background-tint + `#` prefix instead). Full hairline borders or
  background tints only.
- Don't color body/prose text amber, even at "bright" variants — two
  separate rounds of user feedback flagged amber-at-reading-size as hard
  to read; `--fg`/`--fg-dim` exist specifically so this doesn't recur.
- Don't let glow/scanline effects drop body text below 4.5:1 contrast.
- Don't add more accent hues "for delight" — the three dimension colors
  plus the green/amber/red tier system is the complete palette; more would
  dilute the coded meaning.
