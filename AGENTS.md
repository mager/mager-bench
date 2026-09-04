# mager-bench — agent harness notes

This repo's primary harness is **opencode**. `/bench` (`.opencode/commands/bench.md`)
is the canonical workflow; `.claude/skills/run-bench/SKILL.md` mirrors it for
Claude/Eve sessions. If the two disagree, `/bench` wins.

## Wallet rules (learned 2026-09-04 from live AI Gateway logs)

A 50-call GLM-5.3-generate + Sonnet-5-judge window cost ~$0.90, 55% of it the
judge. Uncapped thinking is the burner: Sonnet judge calls hit 5–8k reasoning
tokens ($0.05–0.08 each, 55–83s); GLM generate calls hit 7–9k (127–165s).

1. **Dry-run first for anything paid:** `bench.py --dry-run` prints
   models × challenges × runs + judge calls before spending a token.
2. **Cap thinking on paid runs:** `--thinking-budget 2048` (Anthropic),
   `--reasoning-effort low|medium` (gateway). `low` for generate, `medium` max.
3. **Judge cheap by default.** Free judge (Gemini Flash) for bulk runs; Sonnet
   judge only for final validation. `--judge-max-tokens` defaults to 2048 —
   verdicts are ~300 tokens of JSON, don't raise it to fix judge errors.
4. **Prefer `glm-5.3-promo` for reruns** — heavy prompt caching (120–154k cached
   tokens in live logs), 3–8s vs 25–165s uncached.
5. **Judge errors are crashes, not scores.** 0.0 totals / `judge error` notes,
   or a Sonnet verdict with ~8k reasoning + 1 output token = truncated thinking,
   not a bad model. Re-run the challenge, don't publish the zeros.

## Known failure signatures (live 2026-09-04 GLM-5.3 run)

- **Subject starvation** — `empty response (finish_reason=length)` on big builds
  (doom/slots, `max_tokens=7000`). Thinking models burn the answer budget
  thinking before writing. Fix: `--thinking-headroom 32768` for big-build
  challenges (billed only on actual use). Never merge starved rows.
- **Judge starvation** — Sonnet judge on long responses (debug r3) thinks past
  the judge cap → empty verdict → 0.0 drags the mean (4.9 ± 3.44 observed).
  Fix: `--judge-max-tokens 16384` for the re-run of long-response challenges.
  Same rule: the 0.0 is a crash, re-run, don't merge.

## Board rules

- **Never mock scores.** Every number comes from a real `bench.py` run.
- **One judge per board.** Check `results.json`'s judge first; new runs reuse it.
- **Merge, don't overwrite.** Run to `runs/YYYY-MM-DD-<model>.json`, merge rows
  into `results.json`, refresh `generated_at`. Never `--output results.json`.
- **Commit the paper trail.** `results.json` + `runs/` + `web/data/*` always commit.
- **Publish:** `node web/scripts/sync-results.mjs` (repo root or `web/`),
  `cd web && vercel --prod`, then `git add -A && git commit && git push`.
  sync flips `funding.json` wishlist entries to `scored` automatically.

## Smoke test before a full run

```bash
cd ~/Code/mager-bench
.venv/bin/python -c "from providers import get_provider; print(get_provider('<model-id>').complete('Say OK'))"
```
