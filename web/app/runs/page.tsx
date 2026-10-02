import { Arrow } from "@/components/arrow";
import Link from "next/link";
import { everyday, modelName, date } from "@/lib/everyday";
export const metadata = { title: "Runs | mager-bench 1.2" };
export default function Runs() {
  return (
    <div className="bench-shell">
      <header className="bench-page-heading">
        <h1>Saved attempts</h1>
        <p>
          Every v1.2 attempt, including failed calls. A missing answer never
          becomes a zero.
        </p>
      </header>
      <div className="attempt-list">
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
        <Link className="bench-link" href="/archive/v1.1">
          View archived v1.1 attempts
        </Link>
      </p>
    </div>
  );
}
