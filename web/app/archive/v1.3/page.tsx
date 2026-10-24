import { Arrow } from "@/components/arrow";
import Link from "next/link";
import { EverydayExplorer } from "@/components/everyday-explorer";
import { everyday, modelName, source } from "@/lib/everyday";

const taskNames: Record<string, string> = {
  "build-plan": "Build dependencies",
  "job-selection": "Schedule jobs",
  "split-bill": "Split a bill",
  "clean-csv": "Clean a CSV",
  "meeting-time": "Find a meeting time",
};

export default function Archive13() {
  const latest = everyday.runs.at(-1);
  return (
    <div className="bench-shell bench-compact">
      <header className="bench-intro">
        <h1>1.3 · JavaScript benchmark</h1>
        <p>Five problems for AI models, with 60 tests to check their code.</p>
      </header>
      <section className="current-result" aria-label="Latest result">
        <p>
          {latest ? (
            <>
              <strong>{modelName(latest.model)}</strong>
              {latest.score
                ? ` · ${latest.score.passed}/${latest.score.total} checks passed`
                : " · Incomplete, unscored"}
            </>
          ) : (
            "No runs yet."
          )}
        </p>
        <Link
          className="bench-link"
          href={latest ? `/attempts/${latest.id}` : "/api/v1.3/results"}
        >
          Original data <Arrow />
        </Link>
      </section>
      <section className="everyday-section" id="tasks" aria-label="Tasks">
        <div className="task-list">
          {everyday.tasks.map((task) => (
            <details className="task-row" key={task.id} name="benchmark-task">
              <summary>
                <span className="task-row-title">
                  {taskNames[task.id] ?? task.title}
                </span>
              </summary>
              <EverydayExplorer tasks={[task]} compact />
            </details>
          ))}
        </div>
      </section>
      <section className="everyday-section" id="method" aria-label="Method">
        <details className="bench-details">
          <summary>How it works</summary>
          <div className="method-copy">
            <p>
              Each model gets one try per problem at its lowest supported
              reasoning setting. Each answer runs against 12 tests and earns one
              point per pass. No AI grades the answers.
            </p>
            <p>
              Models have up to 90 seconds per answer and 270 seconds in total.
              The prompt asks for no more than 3,072 tokens per answer.
            </p>
            <p>
              Code runs in QuickJS with 16 MiB of memory and 100 ms of CPU time
              per test, without files or network access. Wrong answers and code
              errors fail tests. A missing answer or failed model call means no
              overall score.
            </p>
            <p>
              These public tests cover a small set of problems. One run is not
              enough to rank models. Times include the local runner.
            </p>
            <a
              className="bench-link"
              href={`${source}/blob/main/docs/mager-bench-1.3.md`}
            >
              Full test rules
            </a>
          </div>
        </details>
      </section>
    </div>
  );
}
