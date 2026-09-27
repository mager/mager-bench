# Counterexample Lab: durable ledger

Design a small, powerful regression suite for the ledger specified below.
Return only a JSON object, without Markdown fences, in this shape:

```json
{"traces":[{"events":[{"op":"inspect"}],"expected":[{"balances":{"a":10,"b":0,"c":0},"revisions":{"a":0,"b":0,"c":0}}]}]}
```

Each trace starts independently with balances `a=10, b=0, c=0`, revisions
`a=0, b=0, c=0`, and an empty request cache. There must be 1–4 nonempty
traces with **at most 12 events TOTAL across all traces**. Each event has
exactly one expected output at the corresponding position. Object key order
does not matter. All numbers must be JSON integers, not booleans or floats.

## Operations and exact outputs

`{"op":"transfer","id":"r1","from":"a","to":"b","amount":3,"expected_revision":0}`

- These six fields are required; no others are allowed. IDs match
  `[A-Za-z0-9_-]{1,24}`. Accounts are `a`, `b`, `c`, or `missing` (an unknown
  account). Amount is an integer 1–20; expected_revision is an integer 0–20.
- The request fingerprint is `(from, to, amount, expected_revision)`.
- Check the cache by ID **before any business validation**. An identical
  fingerprint returns the exact original output without modifying anything.
  A different fingerprint returns `{"status":"conflict"}`, modifying neither
  balances, revisions, nor the original cache entry.
- For a previously unseen ID, validate in this order. If either account is
  unknown, return `{"status":"unknown_account"}`. Otherwise if the accounts
  are equal, return `{"status":"same_account"}`. Otherwise if the source
  revision differs from expected_revision, return `{"status":"stale_revision"}`.
  Otherwise if the source has insufficient funds, return
  `{"status":"insufficient_funds"}`.
- If validation succeeds, move amount from source to destination atomically,
  increment **both** endpoint revisions by one, and return `{"status":"ok"}`.
- Cache the fingerprint and output of every new request, including rejected
  requests. Rejection changes no balances or revisions. Reusing a rejected
  request after circumstances change still returns the original rejection.

`{"op":"inspect"}` returns exactly
`{"balances":{"a":A,"b":B,"c":C},"revisions":{"a":RA,"b":RB,"c":RC}}`,
with current integer values. It changes nothing.

`{"op":"restart"}` returns `{"status":"restarted"}`. It reloads all
committed balances, revisions, and request-cache entries. Every preceding
event is fully committed, even if its output was a rejection. This is a
logical durable reload; there are no partial writes, clocks, or concurrency.

## What earns credit

Your suite is replayed against the correct ledger and eight independently
faulty implementations of this same contract. A trace earns credit only if
**every** expected output agrees with the correct ledger. Such a trace exposes
a faulty implementation when any output differs from your expectations.
Each exposed implementation counts once, regardless of how many tests expose
it. Wrong expectations earn no coverage for that trace. The primary result
is exposed implementations out of eight; explanations and formatting earn
no points. Empty or malformed submissions are unscored failed calls.

Cover interactions between atomicity, revisions, idempotency, rejected
requests, conflicting reuse, and durable recovery within the event budget.
The fault corpus is fixed for version 1.1. It is public benchmark source,
but use only this contract for your answer; do not inspect files or use tools.
