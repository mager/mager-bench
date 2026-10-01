---
name: mager-bench
description: A light experimental workbench for exact, inspectable model evaluations.
colors:
  surface: "oklch(97.9% 0.004 250)"
  raised: "oklch(99.5% 0.002 250)"
  ink: "oklch(24% 0.018 255)"
  secondary: "oklch(48% 0.017 255)"
  accent: "oklch(49% 0.155 36)"
  rule: "oklch(88% 0.008 250)"
  verified: "oklch(42% 0.09 162)"
  mismatch: "oklch(48% 0.17 28)"
typography:
  body: "Manrope, sans-serif"
  code: "IBM Plex Mono, monospace"
---

## Direction

Restrained color: mineral neutrals, near-black ink, and rust for actions and
identity. Green means verified coverage; red means a demonstrated output
mismatch. Color always has accompanying text. A small three-bar mark identifies
the bench. No illustration is required: the oracle-backed interactive trace is
the central visual.

## Typography and layout

Manrope supplies a compact wordmark, 54px desktop / 43px mobile hero, 27px
section titles, and readable body text. IBM Plex Mono is reserved for actual
code, scores, event labels, and small provenance details. Keep prose under 75ch.

The 1184px shell uses 32px desktop and 18px mobile outer space. The homepage
pairs a short introduction with the working example, then moves through a
horizontal specification strip, calibration table, fault list, and archive
explanation. Vary section spacing, and use thin full-width rules for structure.

## Components

- Interactive demo: one bordered workbench, three scenario buttons, numbered
  event buttons, dark code strip, paired correct/faulty outputs, and replay/next.
  Show exact generated outputs; identify examples as hand-authored.
- Calibration: alphabetic model rows, an inspectable link for every attempt,
  numbered per-fault coverage cells with labels and a legend. On mobile use
  stacked table rows, preserving the entire comparison without page overflow.
- Evidence: run lists and trace tables. Put long raw responses and the complete
  contract in accessible native disclosures.
- Archive: full-width explanatory banner on historical boards, models, and
  challenges. Keep original score values and provenance.
- Actions: rust primary, quiet outlined secondary, and text links with small
  directional arrows. Clear visible keyboard focus.

## Guardrails

No glow, scanlines, decorative terminal chrome, gradients, or infinite motion.
No hero score that confuses the old and new contracts. Use flat lists instead
of repeated marketing cards. Allow horizontal scrolling only inside long code
or trace tables. Honor reduced motion and keep basic information available
without interactive controls. Historical CSS token names remain compatible,
but map to the new palette.
