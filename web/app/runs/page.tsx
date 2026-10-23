import { Arrow } from "@/components/arrow";
import Link from "next/link";
import { everyday, modelName, date } from "@/lib/everyday";
export const metadata = { title: "Runs | mager-bench 1.3" };
export default function Runs() {
  return (
    <div className="bench-shell">
      <header className="bench-page-heading">
        <h1>Runs</h1>
        <p>
          Only finished runs get a score.
        </p>
      </header>
      <div className="attempt-list">
        {!everyday.runs.length && (
          <div className="archive-entry">
            <h2>No runs yet</h2>
            <p>
              You can still browse the problems and their tests.
            </p>
            <Link className="bench-link" href="/#tasks">
              See the tests
            </Link>
          </div>
        )}
        {everyday.runs.map((run) => (
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
                ? `${run.score.passed} / ${run.score.total} checks`
                : "Unscored · provider failure"}
            </span>
            <Arrow diagonal />
          </Link>
        ))}
      </div>
      <p className="history-note">
        <Link className="bench-link" href="/archive">
          Earlier versions
        </Link>
      </p>
    </div>
  );
}
