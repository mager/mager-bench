import Link from "next/link";
import { notFound } from "next/navigation";
import { everyday, modelName, date, source } from "@/lib/everyday";
export function generateStaticParams() {
  return everyday.runs.map((r) => ({ id: r.id }));
}
export default async function Attempt({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params,
    run = everyday.runs.find((r) => r.id === id);
  if (!run) notFound();
  return (
    <div className="bench-shell">
      <header className="bench-page-heading">
        <Link className="bench-link" href="/runs">
          All v1.2 attempts
        </Link>
        <h1>{modelName(run.model)}</h1>
        <p>
          {date(run.generated_at)} · {run.reasoning_effort} effort ·{" "}
          {(run.elapsed_ms / 1000).toFixed(1)} seconds elapsed
        </p>
      </header>
      <section className="attempt-summary">
        <h2>
          {run.score
            ? `${run.score.passed} / ${run.score.total} checks passed`
            : "Unscored attempt"}
        </h2>
        {run.error && (
          <>
            <p>
              The provider failed before this benchmark could finish. No overall
              score was assigned.
            </p>
            <pre className="prose-code">{run.error}</pre>
          </>
        )}
        <a className="bench-link" href={`${source}/blob/main/${run.artifact}`}>
          View original artifact
        </a>
      </section>
      <section className="everyday-section">
        <h2>Programs</h2>
        {everyday.tasks.map((task) => {
          const t = run.tasks.find((t) => t.id === task.id);
          return (
            <article className="task-attempt" key={task.id}>
              <div className="bench-section-title">
                <h3>{task.title}</h3>
                <span>
                  {t?.score
                    ? `${t.score.passed} / ${t.score.total} checks`
                    : t
                      ? "Failed call"
                      : "Not run"}
                </span>
              </div>
              {t?.response && (
                <details className="bench-details">
                  <summary>Model’s submitted code</summary>
                  <pre>{t.response}</pre>
                </details>
              )}
              {t?.score?.cases.map((c) => (
                <details className="bench-details" key={c.label}>
                  <summary>
                    {c.passed ? "Passed" : "Failed"} · {c.label}
                  </summary>
                  <div className="case-columns">
                    <div>
                      <h4>Input</h4>
                      <pre>{JSON.stringify(c.input, null, 2)}</pre>
                      <h4>Expected</h4>
                      <pre>{JSON.stringify(c.expected, null, 2)}</pre>
                    </div>
                    <div>
                      <h4>Actual</h4>
                      <pre>{c.error || JSON.stringify(c.actual, null, 2)}</pre>
                    </div>
                  </div>
                </details>
              ))}
            </article>
          );
        })}
      </section>
      <details className="bench-details">
        <summary>Reproduction details</summary>
        <p>Suite SHA-256</p>
        <code className="suite-hash">{run.suite_sha256}</code>
        <p>
          Three calls maximum, 90 seconds per call, 3,072-token prompted target.
          Lowest supported effort. No retries.
        </p>
      </details>
    </div>
  );
}
