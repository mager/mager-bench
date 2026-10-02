import { Arrow } from "@/components/arrow";
import Link from "next/link";
import { EverydayExplorer } from "@/components/everyday-explorer";
import { everyday, modelName, source } from "@/lib/everyday";
export default function Home() {
  const latest = everyday.runs.at(-1);
  return (
    <div className="bench-shell">
      <header className="bench-intro">
        <h1>A quick test of useful code.</h1>
        <p>
          Three everyday programs with difficult edge cases. Each model gets one
          attempt at its lowest reasoning effort. We check whether the code
          works.
        </p>
        <a className="bench-link" href="#tasks">
          Explore the three programs <Arrow />
        </a>
      </header>
      <section className="baseline" aria-labelledby="baseline-heading">
        <div>
          <h2 id="baseline-heading">
            {latest ? modelName(latest.model) : "First benchmark"}
          </h2>
          <p>
            {latest?.score
              ? `${latest.score.passed} of ${latest.score.total} checks passed`
              : "No score yet"}
          </p>
        </div>
        <div className="baseline-note">
          <span
            className={`result-status ${latest?.score ? "is-complete" : ""}`}
          >
            {latest?.score ? "Completed" : "Model unavailable"}
          </span>
          <p>
            {latest?.score
              ? `Saved at ${latest.reasoning_effort} effort. Open the attempt to inspect every result.`
              : "The ChatGPT CLI rejected GPT-6 Sol for this account. The attempt is saved and unscored."}
          </p>
        </div>
        <Link
          className="bench-link"
          href={latest ? `/attempts/${latest.id}` : "/runs"}
        >
          View attempt <Arrow diagonal />
        </Link>
      </section>
      <EverydayExplorer tasks={everyday.tasks} />
      <section className="everyday-section" id="method">
        <div className="bench-section-title">
          <h2>Built to finish quickly</h2>
        </div>
        <dl className="method-grid">
          <div>
            <dt>Three short answers</dt>
            <dd>
              One JavaScript program per task. No retries or model judges.
            </dd>
          </div>
          <div>
            <dt>Lowest effort</dt>
            <dd>
              The runner selects the lowest supported setting. For GPT-6 Sol,
              that’s low.
            </dd>
          </div>
          <div>
            <dt>36 exact checks</dt>
            <dd>
              A check passes when the returned value matches its expected
              output.
            </dd>
          </div>
        </dl>
        <details className="bench-details">
          <summary>Timing, scoring, and limits</summary>
          <div className="method-copy">
            <p>
              Each generation call has a 90-second deadline and a prompted
              target of 3,072 output tokens. Three calls run sequentially, for
              at most 270 seconds of generation waiting. We stop at the first
              provider failure.
            </p>
            <p>
              Programs run in fresh QuickJS contexts with no filesystem or
              network bindings, 16 MiB memory, and a 100 ms CPU limit per case.
              Incorrect values and code errors fail checks. Missing answers and
              provider failures are unscored.
            </p>
            <p>
              These 36 public cases are a small, inspectable sample of
              JavaScript correctness. A single attempt does not establish a
              model ranking. Timings include the local Codex harness and are not
              pure model latency.
            </p>
            <a
              className="bench-link"
              href={`${source}/blob/main/docs/mager-bench-1.2.md`}
            >
              Full protocol on GitHub
            </a>
          </div>
        </details>
      </section>
      <aside className="history-note">
        <p>
          Looking for the older scores? Version 1.1 and the original
          thirteen-task benchmark are preserved in the archive.
        </p>
        <Link className="bench-link" href="/archive">
          Browse the archive
        </Link>
      </aside>
    </div>
  );
}
