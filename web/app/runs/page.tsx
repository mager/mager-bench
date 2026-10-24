import Link from "next/link";
import { Arrow } from "@/components/arrow";
import {
  agentBench,
  evaluations,
  modelName,
  resultLabel,
  duration,
} from "@/lib/agent-v2";
export const metadata = { title: "Runs | mager-bench 2.0" };
function RunList({ runs }: { runs: typeof agentBench.runs }) {
  return (
    <div className="attempt-list">
      {runs.map((run) => (
        <Link className="attempt-row" href={`/v2/runs/${run.id}`} key={run.id}>
          <div>
            <h2>{modelName(run.model)}</h2>
            <p>
              {run.generated_at.slice(0, 10)} · {run.reasoning_effort} ·{" "}
              {duration(run.generation_ms)}
              {run.kind === "evaluation" &&
                ` · seed ${run.seed} · level ${run.level}`}
            </p>
          </div>
          <span>{resultLabel(run)}</span>
          <Arrow diagonal />
        </Link>
      ))}
    </div>
  );
}
export default function Runs() {
  return (
    <div className="bench-shell">
      <header className="bench-page-heading">
        <h1>Runs</h1>
        <p>Saved code. Test results. Time used.</p>
      </header>
      {evaluations.length ? (
        <RunList runs={evaluations} />
      ) : (
        <p className="quiet">No evaluations yet.</p>
      )}
      <details className="bench-details v2-preflights">
        <summary>
          CLI checks · {agentBench.runs.length - evaluations.length}
        </summary>
        <RunList runs={agentBench.runs.filter((r) => r.kind === "preflight")} />
      </details>
      <p className="history-note">
        <Link className="bench-link" href="/archive">
          Earlier versions
        </Link>
      </p>
    </div>
  );
}
