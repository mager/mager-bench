---
name: mager-bench 1.2
description: A clear, fast report for complex everyday coding tasks.
colors:
  bg: "oklch(13% 0.006 270)"
  bg-raised: "oklch(18% 0.01 270)"
  fg: "oklch(94% 0.009 265)"
  report-muted: "#adb5b5"
  report-rule: "#343c3c"
  report-accent: "#a6e2ce"
  status-unavailable: "#edc897"
  expected-surface: "#172420"
  code-surface: "#151919"
  row-hover: "#171c1b"
  selection-ink: "#13211c"
typography:
  display:
    fontFamily: "Manrope, sans-serif"
    fontSize: "clamp(38px, 4.5vw, 54px)"
    fontWeight: 650
    lineHeight: 1.08
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Manrope, sans-serif"
    fontSize: "24px"
    fontWeight: 600
    letterSpacing: "-0.035em"
  title:
    fontFamily: "Manrope, sans-serif"
    fontSize: "20px"
    fontWeight: 600
    letterSpacing: "-0.035em"
  intro:
    fontFamily: "Manrope, sans-serif"
    fontSize: "18px"
    lineHeight: 1.7
  body:
    fontFamily: "Manrope, sans-serif"
    fontSize: "14px"
    lineHeight: 1.8
  label:
    fontFamily: "Manrope, sans-serif"
    fontSize: "13px"
    fontWeight: 500
    letterSpacing: "0"
  code:
    fontFamily: "IBM Plex Mono, monospace"
    fontSize: "12px"
    lineHeight: 1.7
rounded:
  field: "3px"
spacing:
  gap-small: "8px"
  gap-control: "12px"
  gap-copy: "16px"
  gap-content: "24px"
  gap-section: "32px"
components:
  text-link:
    textColor: "{colors.report-accent}"
  text-link-hover:
    textColor: "{colors.fg}"
  task-button:
    textColor: "{colors.report-muted}"
    padding: "0 0 20px"
  task-button-selected:
    textColor: "{colors.report-accent}"
  case-select:
    backgroundColor: "{colors.bg-raised}"
    textColor: "{colors.fg}"
    rounded: "{rounded.field}"
    padding: "8px 35px 8px 12px"
  expected-answer:
    backgroundColor: "{colors.expected-surface}"
    textColor: "{colors.fg}"
    padding: "20px 24px"
  code-panel:
    backgroundColor: "{colors.code-surface}"
    textColor: "{colors.fg}"
    typography: "{typography.code}"
    padding: "20px"
  version-tag:
    textColor: "{colors.report-accent}"
    padding: "3px 7px"
  navigation:
    textColor: "{colors.report-muted}"
  navigation-current:
    textColor: "{colors.fg}"
  disclosure:
    padding: "18px 0"
---

# Design System: mager-bench 1.2

## Overview

**Creative North Star: "Software test report"**

A software test report viewed at a desk at night. Dark surfaces, readable Manrope, thin rules, and restrained mint links give exact inputs and results room to be understood. The active system is code-led and uses no shipping raster imagery or approved visual comp.

This document records the implemented v1.2 system. The shared header and footer use this system; historical benchmark content retains its legacy styles, including Barlow Condensed, sports graphics, and older score colors. Those archival treatments are not defaults for new active screens.

**Key Characteristics:**

- Readable sentence-case headings and plain task names.
- Flat rows and literal code, with clearly labeled expected results.
- Visible control states and local scrolling for long code.

## Colors

The palette is near-black with quiet gray text, mint interaction cues, and a warm unavailable-status accent. Frontmatter preserves the source formats: inherited root colors remain OKLCH; report colors remain hex.

### Primary

- **Report mint** (`report-accent`) identifies links, selected task buttons, completed statuses, keyboard focus, and expected-result labels.

### Secondary

- **Warm status** (`status-unavailable`) marks the saved but unavailable model state, accompanied by an explicit text label.

### Neutral

- **Night background** (`bg`) and **raised field** (`bg-raised`) come from the shared root stylesheet.
- **Clear foreground** (`fg`), **muted report text** (`report-muted`), and **report rule** (`report-rule`) establish readable hierarchy and thin section divisions.
- **Expected surface** gently tints the published answer; **code surface** holds exact input/output and prompts.
- **Row hover** marks linked attempt and archive rows; **selection ink** supports selected text on mint.

**The Labeled State Rule.** Status color always accompanies a meaningful text label; an unavailable attempt remains visibly unscored.

## Typography

Manrope is the active display and body family. IBM Plex Mono is the code family. Both are loaded in `web/app/layout.tsx`; CSS uses their font variables with generic fallbacks. Barlow Condensed remains loaded for historical content only.

Display headings use the fluid `display` role. Section headings use `headline`; example headings use `title`. Intro prose is comfortable at a maximum of (64ch); method copy extends to (72ch). The report uses tabular numerals. Active headings preserve sentence case and balanced wrapping.

At the phone breakpoint, intro copy becomes (16px), section headings become (22px), and task labels become (14px) with a (1.5) line height. Secondary page titles have their own observed size (`clamp(34px, 5vw, 50px)`) and line height (1.2).

## Layout

The active shell is centered at `min(1080px, calc(100% - 64px))`. Wide rows and horizontal rules organize the report; source and expected output sit in equal columns with a (24px) gap. The three task buttons remain a three-column group. Method notes use three columns with (32px) gaps.

At (700px) and below, the shell uses (18px) side gutters. Navigation wraps into a second row; model availability, code columns, and method notes stack. Task descriptions hide while their labels stay visible. The case selector becomes full width. Attempt rows move to two columns with metadata on the next row. Long code scrolls inside its own panel, with a maximum height of (440px); prompt disclosures wrap and have no maximum height.

## Elevation & Depth

Active v1.2 uses no shadows. Depth comes from flat surface fills, thin rules, and spacing. Expected results have a tinted field; code and controls have distinct dark surfaces. Hover changes color or background without moving elements.

Inherited transitions animate color, background color, and border color over (0.16s ease). The page inherits smooth anchor scrolling and switches to automatic scrolling when reduced motion is requested. No new animation grammar is introduced.

## Shapes

Report rows, code panels, tags, and result fields are square. The native case select is slightly rounded using `rounded.field`. Section and code borders are thin (1px); selected task buttons use an accent bottom border (2px). Keyboard focus inside the report uses a mint outline (2px) with an offset (5px).

## Components

### Task buttons

Plain text selectors with a short descriptive line. Default text is muted; the selected label and bottom rule are mint. Hover text becomes foreground. Selection uses `aria-pressed`; choosing a program resets the test-case selection. Desktop minimum height is (96px), dropping to (64px) on phones. These are the active button pattern; there is no filled primary CTA on the active homepage.

### Case selector

A labeled native select on a raised dark surface, with a thin report-rule border and visible report focus treatment. It has a minimum height of (44px) and stays within its container. No custom text-input pattern exists on this surface.

### Expected result and code panels

The expected-result field pairs a small mint label with a readable answer, announced through a polite live region. The adjacent input and exact-output panels use the code role and local scrolling. Each has an explicit heading; the fixture explanation distinguishes these from model responses. These flat containers are the active card-like pattern.

### Links and navigation

Report links are mint, underlined, and brighten on hover. The header is a text wordmark with a small outlined version tag. Navigation uses muted text, brightens on hover, and uses `aria-current` for Runs and Archive. The footer retains quiet text links. Focus uses the shared report outline.

### Disclosures and saved attempts

Native details/summary elements reveal exact prompts and method notes. Summary hit areas remain focusable, with room below when open. Saved attempts and archive entries are broad linked rows divided by rules; their hover surface is subtle. Each saved attempt's real status determines its label and evidence links.

## Do's and Don'ts

### Do:

- Do use Manrope for active headings, prose, and controls; use IBM Plex Mono for code.
- Do preserve visible focus, selected-state borders, and text labels alongside status colors.
- Do distinguish published fixtures from saved model answers and keep unscored attempts explicit.
- Do keep familiar task language, fast runs, and the lowest supported effort clear in the interface.
- Do preserve historical routes and their original presentation without blending benchmark versions.

### Don't:

- Don't revive the basketball or Counterexample identity on active v1.2 surfaces.
- Don't add promotional slogans, decorative imagery, simulated results, or fictional live statuses.
- Don't turn provider failures into zero scores or style a single run as a reliable ranking.
- Don't replace the report's flat rows with decorative elevated cards.
