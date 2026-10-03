import Link from "next/link";
import { EverydayExplorer } from "@/components/everyday-explorer";
import { archivedEveryday, modelName, date } from "@/lib/everyday";
export const metadata = { title: "Version 1.2 archive | mager-bench" };
export default function Archive12() {
  return (
    <div className="bench-shell">
      <header className="bench-page-heading">
        <h1>1.2 · Three everyday programs</h1>
        <p>
          The original 36 checks are frozen. Version 1.3 keeps these tasks and
          adds dependency-graph planning and budgeted scheduling. Their overall
          scores are separate.
        </p>
        <Link className="bench-link" href="/">
          Explore the current suite
        </Link>
      </header>
      <div className="attempt-list">
        {archivedEveryday.runs.map((run) => (
          <Link
            className="attempt-row"
            href={`/attempts/${run.id}`}
            key={run.id}
          >
            <div>
              <h2>{modelName(run.model)}</h2>
              <p>
                {date(run.generated_at)} · {run.reasoning_effort} effort
              </p>
            </div>
            <span>
              {run.score
                ? `${run.score.passed} / ${run.score.total}`
                : "Unscored · provider failure"}
            </span>
          </Link>
        ))}
      </div>
      <EverydayExplorer tasks={archivedEveryday.tasks} />
      <p className="history-note">
        <a className="bench-link" href="/api/v1.2/results">
          Original v1.2 data
        </a>
      </p>
    </div>
  );
}
