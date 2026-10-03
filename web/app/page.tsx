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
          Two algorithmic problems and three everyday programs. Each model gets
          one attempt at its lowest reasoning effort. We check whether the code
          works.
        </p>
        <a className="bench-link" href="#tasks">
          Explore the five programs <Arrow />
        </a>
      </header>
      <section className="baseline" aria-labelledby="baseline-heading">
        <div>
          <h2 id="baseline-heading">
            {latest ? modelName(latest.model) : "Five tasks, 60 checks"}
          </h2>
          <p>
            {latest?.score
              ? `${latest.score.passed} of ${latest.score.total} checks passed`
              : "No v1.3 model results yet"}
          </p>
        </div>
        <div className="baseline-note">
          <span
            className={`result-status ${latest?.score ? "is-complete" : ""}`}
          >
            {latest
              ? latest.score
                ? "Completed"
                : "Unscored"
              : "Ready to benchmark"}
          </span>
          <p>
            {latest?.score
              ? `Saved at ${latest.reasoning_effort} effort. Open the attempt to inspect every result.`
              : latest
                ? "The attempt did not finish. Its failure is saved without an overall score."
                : "The graph and optimization tasks pass reference checks. Model calibration is still pending."}
          </p>
        </div>
        <Link
          className="bench-link"
          href={latest ? `/attempts/${latest.id}` : "/runs"}
        >
          View attempts <Arrow diagonal />
        </Link>
      </section>
      <EverydayExplorer tasks={everyday.tasks} />
      <section
        className="everyday-section"
        aria-labelledby="difficulty-heading"
      >
        <h2 id="difficulty-heading">Where shortcuts fail</h2>
        <div className="method-copy">
          <p>
            A dependency graph with 40 layers has over a trillion possible
            paths. The program must reuse computed results. Enumerating every
            path exceeds the time limit.
          </p>
          <p>
            In the scheduling task, one job pays 10, but two compatible jobs pay
            12 together. The full problem also has a spending budget and
            cooldown periods. Picking the biggest job first gives the wrong
            answer.
          </p>
          <p>
            The 80-job case makes exhaustive subset search impractical. These
            cases test algorithm choice as well as edge cases; how models
            perform is still unmeasured.
          </p>
        </div>
      </section>
      <section className="everyday-section" id="method">
        <div className="bench-section-title">
          <h2>Built to finish quickly</h2>
        </div>
        <dl className="method-grid">
          <div>
            <dt>Five short answers</dt>
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
            <dt>60 exact checks</dt>
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
              target of 3,072 output tokens. Five calls share the same total
              budget, for at most 270 seconds of generation waiting. We stop at
              the first provider failure.
            </p>
            <p>
              Programs run in fresh QuickJS contexts with no filesystem or
              network bindings, 16 MiB memory, and a 100 ms CPU limit per case.
              Incorrect values and code errors fail checks. Missing answers and
              provider failures are unscored.
            </p>
            <p>
              These 60 public cases are a small, inspectable sample of
              JavaScript correctness. A single attempt does not establish a
              model ranking. Timings include the local Codex harness and are not
              pure model latency.
            </p>
            <a
              className="bench-link"
              href={`${source}/blob/main/docs/mager-bench-1.3.md`}
            >
              Full protocol on GitHub
            </a>
          </div>
        </details>
      </section>
      <aside className="history-note">
        <p>
          Looking for the older scores? Versions 1.2, 1.1, and the original
          thirteen-task benchmark are preserved in the archive.
        </p>
        <Link className="bench-link" href="/archive">
          Browse the archive
        </Link>
      </aside>
    </div>
  );
}
