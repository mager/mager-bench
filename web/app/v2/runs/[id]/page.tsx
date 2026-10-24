import Link from "next/link";
import { notFound } from "next/navigation";
import { agentBench, modelName, resultLabel, duration } from "@/lib/agent-v2";
export function generateStaticParams() {
  return agentBench.runs.map(({ id }) => ({ id }));
}
export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const run = agentBench.runs.find((r) => r.id === id);
  return {
    title: run
      ? `${modelName(run.model)} run | mager-bench 2.0`
      : "Run not found",
  };
}
export default async function RunPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const run = agentBench.runs.find((r) => r.id === id);
  if (!run) notFound();
  return (
    <div className="bench-shell">
      <header className="bench-page-heading">
        <Link className="bench-link" href="/runs">
          ← All runs
        </Link>
        <h1>{modelName(run.model)}</h1>
        <p>{resultLabel(run)}</p>
        <div className="v2-facts">
          <span>{run.generated_at.slice(0, 10)}</span>
          <span>{duration(run.generation_ms)} agent time</span>
          <span>{run.reasoning_effort} effort</span>
          {run.kind === "evaluation" && (
            <>
              <span>Seed {run.seed}</span>
              <span>Level {run.level}</span>
            </>
          )}
        </div>
        {run.score && (
          <p>
            {run.score.tasks_passed} / {run.score.tasks_total} projects passed
            both work orders.
          </p>
        )}
        <a className="bench-link" href={run.raw_url} download>
          Download full evidence
        </a>
      </header>
      {run.error && (
        <div className="v2-failure">
          <strong>Unscored</strong>
          <p>{run.error}</p>
          {run.probe?.stderr && <pre>{run.probe.stderr}</pre>}
        </div>
      )}
      {run.kind === "preflight" && (
        <p className="quiet">
          File-edit check only. This is not a benchmark score.
        </p>
      )}
      {run.tasks.map((task) => (
        <section className="everyday-section" key={task.id}>
          <h2>{agentBench.tasks.find((t) => t.id === task.id)?.title}</h2>
          {task.phases.map((phase) => (
            <details className="bench-details" key={phase.phase}>
              <summary>
                Work order {phase.phase} ·{" "}
                {phase.score
                  ? `${phase.score.passed} / ${phase.score.total}`
                  : "Unscored"}{" "}
                · {duration(phase.elapsed_ms ?? 0)}
              </summary>
              {phase.error && <p className="v2-failure">{phase.error}</p>}
              {phase.score && (
                <div className="v2-facts">
                  {Object.entries(phase.score.groups).map(([name, score]) => (
                    <span key={name}>
                      {name}: {score.passed}/{score.total}
                    </span>
                  ))}
                </div>
              )}
              {phase.score && phase.score.failures.length > 0 && (
                <details className="bench-details">
                  <summary>
                    Failed cases · first {phase.score.failures.length}
                  </summary>
                  {phase.score.failures.map((check) => (
                    <div className="v2-check" key={check.id}>
                      <h3>{check.id}</h3>
                      {check.error && <p>{check.error}</p>}
                      <pre>
                        {JSON.stringify(
                          {
                            input: check.input,
                            expected: check.expected,
                            actual: check.actual,
                          },
                          null,
                          2,
                        )}
                      </pre>
                    </div>
                  ))}
                </details>
              )}
              {phase.diff && (
                <details className="bench-details">
                  <summary>Code changes</summary>
                  <pre>{phase.diff}</pre>
                </details>
              )}
              {phase.sources && (
                <details className="bench-details">
                  <summary>Submitted code</summary>
                  {Object.entries(phase.sources).map(([path, code]) => (
                    <div className="v2-check" key={path}>
                      <h3>{path}</h3>
                      <pre>{code}</pre>
                    </div>
                  ))}
                </details>
              )}
              {phase.response && (
                <details className="bench-details">
                  <summary>Agent response</summary>
                  <pre className="v2-contract">{phase.response}</pre>
                </details>
              )}
              <details className="bench-details">
                <summary>Session data</summary>
                <pre>
                  {JSON.stringify(
                    {
                      commands: phase.command_count,
                      tokens: phase.usage,
                      integrity_errors: phase.integrity_errors,
                    },
                    null,
                    2,
                  )}
                </pre>
              </details>
            </details>
          ))}
        </section>
      ))}
      <details className="bench-details v2-preflights">
        <summary>Runtime and suite</summary>
        <pre>
          {JSON.stringify(
            {
              suite_sha256: run.suite_sha256,
              runtime: run.runtime,
              elapsed_ms: run.elapsed_ms,
            },
            null,
            2,
          )}
        </pre>
      </details>
    </div>
  );
}
