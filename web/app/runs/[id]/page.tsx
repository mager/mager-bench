import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Arrow } from "@/components/arrow";
import {
  lab,
  dateLabel,
  sourceRoot,
  pretty,
  type LedgerEvent,
  type LedgerOutput,
} from "@/lib/counterexample";

type Props = { params: Promise<{ id: string }> };
export function generateStaticParams() {
  return lab.runs.map((run) => ({ id: run.id }));
}
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const run = lab.runs.find((item) => item.id === id);
  return {
    title: run
      ? `${run.modelName}, attempt ${id.match(/r(\d+)$/)?.[1]} | mager-bench`
      : "Run not found",
  };
}
export default async function RunPage({ params }: Props) {
  const { id } = await params;
  const run = lab.runs.find((item) => item.id === id);
  if (!run) notFound();
  const submission = run.score
    ? (JSON.parse(run.response) as {
        traces: { events: LedgerEvent[]; expected: LedgerOutput[] }[];
      })
    : null;
  return (
    <div className="site-width">
      <header className="page-header">
        <Link className="text-link mb-7" href="/runs">
          ← All attempts
        </Link>
        <div className="eyebrow">
          Counterexample Lab / Attempt {id.match(/r(\d+)$/)?.[1]}
        </div>
        <h1>{run.modelName}</h1>
        <p>
          {dateLabel(run.generated_at)} · {run.reasoning_effort} reasoning ·
          Codex CLI · {run.status}
        </p>
      </header>
      <div className="spec-strip">
        <div>
          <strong>{run.score ? `${run.score.killed} / 8` : "Unscored"}</strong>
          <span>faults exposed</span>
        </div>
        <div>
          <strong>{run.score?.events_used ?? "—"} / 12</strong>
          <span>events used</span>
        </div>
        <div>
          <strong>
            {run.score
              ? `${run.score.valid_traces} / ${run.score.total_traces}`
              : "—"}
          </strong>
          <span>valid traces</span>
        </div>
        <div>
          <strong>{(run.subject_elapsed_ms / 1000).toFixed(1)} sec</strong>
          <span>wall-clock subject time</span>
        </div>
      </div>
      <section className="section">
        <div className="section-heading">
          <div>
            <h2>Which faults did it find?</h2>
            <p>
              Exposure means at least one fully valid trace made this faulty
              ledger disagree with the reference.
            </p>
          </div>
        </div>
        <ul className="fault-status-list">
          {lab.faults.map((fault, index) => (
            <li key={fault.id}>
              <div>
                <span className="mr-3 text-fg-dim">0{index + 1}</span>
                {fault.name}
              </div>
              <span
                className={
                  run.score?.killed_mutants.includes(fault.id)
                    ? "text-green"
                    : "text-fg-dim"
                }
              >
                {run.score
                  ? run.score.killed_mutants.includes(fault.id)
                    ? "Exposed"
                    : "Not exposed"
                  : "Unscored"}
              </span>
            </li>
          ))}
        </ul>
      </section>
      {submission?.traces.map((trace, index) => (
        <section className="section" key={index}>
          <div className="section-heading">
            <div>
              <div className="eyebrow">The submitted test</div>
              <h2>Trace {index + 1}</h2>
              <p>
                {run.score?.trace_results[index].oracle_match
                  ? "Every expected output matches the reference ledger."
                  : "At least one expectation differs from the reference. This trace earns no coverage."}
              </p>
            </div>
            <span className="version-pill">{trace.events.length} events</span>
          </div>
          <div className="table-scroll">
            <table className="trace-table">
              <thead>
                <tr>
                  <th scope="col">#</th>
                  <th scope="col">Event</th>
                  <th scope="col">Model’s expected output</th>
                </tr>
              </thead>
              <tbody>
                {trace.events.map((event, eventIndex) => (
                  <tr key={eventIndex}>
                    <td>{String(eventIndex + 1).padStart(2, "0")}</td>
                    <td>
                      <pre>{pretty(event)}</pre>
                    </td>
                    <td>
                      <pre>{pretty(trace.expected[eventIndex])}</pre>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {!run.score?.trace_results[index].oracle_match && (
            <pre className="code-panel mt-4">
              {pretty(run.score?.trace_results[index].first_mismatch)}
            </pre>
          )}
        </section>
      ))}
      <section className="section">
        <div className="section-heading">
          <div>
            <h2>The original response</h2>
            <p>
              Preserved verbatim from the subject. The source artifact also
              includes the prompt and complete scoring result.
            </p>
          </div>
          <a
            className="text-link"
            href={`${sourceRoot}/blob/main/runs/v1.1/${id}.json`}
          >
            Source artifact
            <Arrow diagonal />
          </a>
        </div>
        {run.error && <p className="prose-copy mb-4">{run.error}</p>}
        <details className="details-panel">
          <summary>Open raw model response</summary>
          <pre className="code-panel whitespace-pre-wrap break-all">
            {run.response || "No response was returned."}
          </pre>
        </details>
        <p className="section-note break-all font-mono">
          Suite SHA-256: {lab.suiteHash}
        </p>
      </section>
      <div className="archive-teaser">
        <Link className="text-link" href="/challenges#method">
          Read the scoring method
          <Arrow />
        </Link>
        <Link className="text-link" href="/runs">
          Compare the other attempts
          <Arrow />
        </Link>
      </div>
    </div>
  );
}
