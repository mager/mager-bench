# Additional v1.1 calibration

Plan recorded before subject generation on October 1, 2026 (America/Chicago).

- Initial candidates: `codex-cli/gpt-6.1-sol`, `codex-cli/gpt-6-luna`, and
  `codex-cli/gpt-5.6-terra`, listed in the local subscription model catalogue.
- Preflight rejected GPT-6.1 Sol and GPT-6 Luna as unsupported for this ChatGPT
  account. Before any scored calls, the final subjects became
  `codex-cli/gpt-5.6-terra`, `codex-cli/gpt-5.6-luna`, and `codex-cli/gpt-5.5`.
  All three passed `Say OK`; all five smoke responses are retained in `preflight/`.
- Three independent fresh sessions per subject, serial and interleaved in that
  order: Terra / Luna / GPT-5.5, repeated three times.
- Nine planned subject calls, zero judge calls. ChatGPT subscription only.
- Reasoning effort: `low`; output target: 4096 tokens, prompted rather than capped.
- Same frozen 1.1 prompt, oracle, mutants, runner, and provider as September 30.
- Retain every attempt with a new filename, including unscored failures. Any
  retries are separate artifacts and are not substituted for weaker results.
- Report all scores, oracle correctness, failures, and per-fault coverage.
  This is preliminary calibration on one narrow task, not a general ranking.

## Reproduction and source identity

The frozen `providers.py` catalogue contains only the original two subscription
subjects. `subscription_models_v1_1.py` adds the candidate identities in memory
and delegates to the unchanged `bench_v1_1.main`. It uses the same
`CodexCLIProvider`, without changing the call or scoring implementation.
The supplementary catalogue is committed separately from the frozen files;
the original suite fingerprint does not cover this metadata-only launcher.

```bash
codex login status
.venv/bin/python subscription_models_v1_1.py --model codex-cli/gpt-5.6-terra --dry-run
.venv/bin/python -c "from subscription_models_v1_1 import register_models; register_models(); from providers import get_provider; print(get_provider('codex-cli/gpt-5.6-terra').complete('Say OK'))"
.venv/bin/python subscription_models_v1_1.py --model codex-cli/gpt-5.6-terra \
  --reasoning-effort low --output runs/v1.1/2026-10-01-codex-cli-gpt-5.6-terra-r1.json
```

Repeat the dry run and smoke test for each subject before its first attempt.
Use r1, r2, and r3 for each subject's planned slots. Do not overwrite outputs.

Frozen suite SHA-256:
`a56a4aadf5b20a319c7a57309608477d9e523da3d99c37a69bb6353f6b16f0c1`.
Frozen source revision: `6696e55` (all five fingerprinted files unchanged).

Supplementary catalogue SHA-256:
`919b2729bb084c44ef44fbec622b0f45799b753c927999d8088d739bc6e83f97`.

## Execution note

Luna r3 returned an out-of-range `expected_revision`; the runner saved the full
response as an unscored schema failure and the serial batch stopped. Terra had
completed all three planned slots. Resume only the missing GPT-5.5 r3 slot,
then run one additional fresh Luna session as r4. That fourth attempt is an
explicit retry, not a replacement for r3; both remain in the published log.
This adds one subject call to the original nine-call plan, with no judge calls.

## Completed observations

| Subject | Planned attempts r1 / r2 / r3 | Additional retry | Graded traces correct | Unscored failures |
|---|---|---|---|---|
| GPT-5.6 Terra | 6/8, 6/8, 6/8 | None | 4/4 | 0 |
| GPT-5.6 Luna | 7/8, 5/8, unscored | r4: 6/8 | 8/8 | 1 |
| GPT-5.5 | 6/8, 6/8, 5/8 | None | 9/9 | 0 |

Ten subject attempts produced nine completed scores and one unscored failure.
All 21 graded traces matched the oracle. Luna r3 used `expected_revision: 99`,
outside the allowed 0–20 range; its entire submission is unscored. Its r4 retry
passed the schema and oracle checks. We did not repair model-authored output.
The two unsupported-model smoke checks are separate availability failures,
not scored challenge attempts. Five smoke calls plus ten subject calls were
made through the subscription; zero judge calls or API fallback calls.

### Fault coverage across the three completed attempts per new subject

| Fault | Terra | Luna | GPT-5.5 |
|---|---|---|---|
| Lost request history | 3/3 | 3/3 | 3/3 |
| Forgotten rejection | 3/3 | 3/3 | 3/3 |
| Unchecked payload | 3/3 | 3/3 | 3/3 |
| Revalidated retry | 3/3 | 3/3 | 3/3 |
| Partial transfer | 0/3 | 0/3 | 0/3 |
| Missing revision | 3/3 | 3/3 | 3/3 |
| Stale write | 1/3 | 2/3 | 2/3 |
| Overwritten history | 2/3 | 1/3 | 0/3 |

Luna's completed-attempt denominator excludes its unscored r3, which remains
visible in the attempt log and failure count. None of the nine completed new
attempts exposed partial-transfer mutation, the same gap observed in the first
six attempts. These small samples do not establish a model ranking.

The exporter independently regraded all completed responses, preserving the
original suite fingerprint and settings. The site now retains 16 challenge
attempts across five subjects, including one unscored failure. Its conservative
`calibrationReady` flag remains false because the historical failure is retained;
the retry does not erase that evidence.
