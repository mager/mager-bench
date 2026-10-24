import Link from "next/link";
import { Arrow } from "@/components/arrow";
import {
  agentBench,
  evaluations,
  modelName,
  resultLabel,
} from "@/lib/agent-v2";

export default function Home() {
  const latest = evaluations[0];
  return (
    <div className="bench-shell bench-compact">
      <header className="bench-intro">
        <h1>Can it fix the code?</h1>
        <p>Three JavaScript projects. Fix a bug, then handle a change.</p>
        <div className="v2-facts">
          <span>192 checks</span>
          <span>10-minute limit</span>
          <span>Codex CLI</span>
        </div>
      </header>
      <section className="current-result" aria-label="Latest result">
        <p>
          {latest ? (
            <>
              <strong>{modelName(latest.model)}</strong> · {resultLabel(latest)}
            </>
          ) : (
            "No scored runs yet."
          )}
        </p>
        <Link
          className="bench-link"
          href={latest ? `/v2/runs/${latest.id}` : "/runs"}
        >
          View runs <Arrow />
        </Link>
      </section>
      <section className="everyday-section" id="tasks" aria-label="Tasks">
        <div className="task-list">
          {agentBench.tasks.map((task) => (
            <details className="task-row" key={task.id} name="benchmark-task">
              <summary>
                <span className="task-row-title">{task.title}</span>
              </summary>
              <div className="v2-task-body">
                <p>{task.summary}</p>
                {task.phases.map((phase, index) => (
                  <details className="bench-details" key={index}>
                    <summary>
                      Work order {index + 1}: {index === 0 ? "Fix" : "Change"} ·
                      32 checks
                    </summary>
                    <pre className="v2-contract">{phase}</pre>
                  </details>
                ))}
                <a className="bench-link" href={`/api/v2/tasks/${task.id}`}>
                  Full prompts and starter code
                </a>
              </div>
            </details>
          ))}
        </div>
      </section>
      <section className="everyday-section" id="method" aria-label="Method">
        <details className="bench-details">
          <summary>How it works</summary>
          <div className="method-copy">
            <p>
              Codex edits files and runs tests. Each project has two work
              orders, with a fresh session for each. The code carries over.
            </p>
            <p>
              32 checks per work order. One point per pass. No AI judge. Tests
              include fixed cases, generated inputs, and regression checks.
            </p>
            <p>
              ChatGPT subscription. Lowest supported effort. Up to two minutes
              per session, ten minutes total. A failed session leaves the run
              unscored.
            </p>
            <p>
              Compare the same seed, level, suite hash, and runtime. These are
              small, public test projects. One run is not a ranking.
            </p>
            <Link className="bench-link" href="/method">
              Full test rules
            </Link>
          </div>
        </details>
      </section>
    </div>
  );
}
