import Link from "next/link";
export const metadata = { title: "Archive | mager-bench" };
export default function Archive() {
  return (
    <div className="bench-shell">
      <header className="bench-page-heading">
        <h1>Earlier benchmarks</h1>
        <p>
          The questions changed. The original prompts, answers, and scoring
          records are still here. Scores from different versions are not
          comparable.
        </p>
      </header>
      <div className="attempt-list">
        <Link className="archive-entry" href="/archive/v1.2">
          <h2>1.2 · Three everyday programs</h2>
          <p>
            Weighted bills, contact CSVs, and meeting times. The first GPT-6 Sol
            attempt failed at the provider and remains unscored.
          </p>
          <span className="bench-link">View v1.2 tasks and attempt</span>
        </Link>
        <Link className="archive-entry" href="/archive/v1.1">
          <h2>1.1 · Counterexample Lab</h2>
          <p>
            Models wrote test traces to expose eight ledger faults. All 16
            calibration attempts are preserved.
          </p>
          <span className="bench-link">View calibration runs</span>
        </Link>
        <Link className="archive-entry" href="/archive/subscription">
          <h2>Original thirteen tasks</h2>
          <p>
            The ChatGPT subscription board, scored by GPT-5.6 Sol on a 0–10
            scale.
          </p>
          <span className="bench-link">View subscription board</span>
        </Link>
        <Link className="archive-entry" href="/archive/sonnet-5">
          <h2>Earlier API board</h2>
          <p>
            The original runs using Sonnet 5 as judge. Kept separate from the
            subscription results.
          </p>
          <span className="bench-link">View Sonnet 5 board</span>
        </Link>
      </div>
    </div>
  );
}
