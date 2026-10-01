# First v1.1 calibration

Plan recorded before subject generation on September 30, 2026 (America/Chicago).

- Subjects: `codex-cli/gpt-6-astra`, `codex-cli/gpt-5.6-sol`.
- Three independent fresh sessions per subject, interleaved Astra/Sol, serial.
- Reasoning effort: `low`; output target: 4096 tokens, prompted rather than capped.
- Frozen v1.1 prompt, oracle, mutants, runner, and provider; identical suite hashes required.
- Six subject calls, zero judge calls. ChatGPT subscription only.
- Preserve every response and any failed attempt. No best-of selection.
- Report all attempts, per-model score ranges, and per-fault coverage. Treat this
  small calibration as preliminary, not evidence of general model superiority.
- If a call fails, retain it and resolve the failure before publishing a comparison.
  Any retry must be labeled separately and must not silently replace an attempt.

Authentication, both dry runs, both model smoke tests, and all 41 harness tests
passed before starting. This design session's hand-derived fixture is not a model
result and is excluded from calibration.

The execution session was interrupted after three saved attempts (Astra r1/r2
and Sol r1). Those artifacts were retained. Only missing planned output slots
were resumed; no saved attempt was replaced. Any interrupted call without a
final artifact is unscored and is not included in the completed-sample count.

## Completed observations

All six saved attempts completed and every submitted trace matched the oracle.
Astra exposed 7/8, 7/8, and 7/8 faults; Sol exposed 7/8, 6/8, and 5/8. Neither
model exposed `debit_before_credit_validation` in any of the three attempts.
No completed artifact was discarded. Each result was independently regraded
by the website exporter before publication. The frozen suite hash is
`a56a4aadf5b20a319c7a57309608477d9e523da3d99c37a69bb6353f6b16f0c1`.

These are counts on one narrow contract, not a conversion of the legacy
0–10 scores or proof of general model superiority. More subjects and repeated
calibration are needed before deciding whether the next version needs a larger
fault corpus or different event budget. Such scoring changes must become 1.2.
