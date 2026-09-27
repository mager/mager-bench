# mager-bench 1.1: make the model find the bug

Draft · September 26, 2026

Astra got 9.3 on mager-bench. Four of the thirteen task totals were perfect.
That's one run, with a model judge, so it doesn't prove the benchmark is solved.
But it does make me wonder how much signal is left near the top.

For 1.1, I used Astra to help design **Counterexample Lab**. I'm also retiring
FizzBuzz, binary search, and the simple refactoring task from the active suite.
Their prompts and results stay archived; the other ten old tasks remain optional
baselines. Counterexample Lab is the first active 1.1 track.

The model gets the rules for a tiny money-transfer ledger. It has to write a
regression suite with exact expected results: at most four scenarios and twelve
events total. Transfers, retries, stale revisions, failures, and restarts all
interact. The budget forces the model to choose sequences that reveal something.

Then we run its answer against a reference ledger and eight deliberately broken
versions. Did it catch the forgotten failed request? The conflict that replaced
the original request history?

Correct expectations come first. A test that misunderstands the contract earns
no credit. Each distinct bug caught counts once. The result is bugs caught out
of eight, with no model judge grading the prose.

My bet is that compact tests with exact expectations will reveal gaps that
another implementation prompt misses. We haven't run the models on 1.1 yet.

The [specification](../docs/mager-bench-1.1.md) and
[runner](../bench_v1_1.py) are in the repo. Next comes calibration: repeated runs,
matching reasoning effort, and the same frozen test.
The faults are public, so this isn't future-proof. When the next meaningful
change is ready, we'll call it 1.2.
