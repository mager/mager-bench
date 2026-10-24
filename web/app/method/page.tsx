import { agentBench } from "@/lib/agent-v2";
export const metadata = { title: "Test rules | mager-bench 2.0" };
export default function Method() {
  return (
    <article className="bench-shell v2-method">
      <header className="bench-page-heading">
        <h1>Test rules</h1>
        <p>mager-bench 2.0</p>
      </header>
      <section>
        <h2>The work</h2>
        <p>
          Three small JavaScript repositories: an event ledger, a build cache,
          and an access policy engine. Each starts with broken code and two
          visible tests. Codex can read files, edit code, and run local tests.
        </p>
        <p>
          The first work order fixes a bug. The second adds a requirement. Each
          order starts a fresh Codex session. Source files and added tests carry
          over; conversation history does not. The agent does not receive
          evaluation results between orders.
        </p>
      </section>
      <section>
        <h2>The score</h2>
        <p>
          Each order has 32 checks: eight fixed boundary cases, plus generated
          cases. The second order includes eight regression cases. Each check
          earns one point. A project passes only when all 64 checks pass. The
          full run has 192 checks. No model judges the code.
        </p>
        <p>
          Python computes expected results. A separate JavaScript reference
          implementation checks the test design. Reference scores are test
          fixtures, never model results. The exporter reruns saved code before
          it publishes a score.
        </p>
      </section>
      <section>
        <h2>The limits</h2>
        <p>
          ChatGPT subscription only, through Codex CLI. The runner selects the
          lowest supported effort from the local catalog. Six sessions share 600
          seconds of agent time, with at most 120 seconds each. Time includes
          CLI startup, generation, and tool use. Local grading is outside this
          budget.
        </p>
        <p>
          The runner does not retry sessions, change models, or use an API key.
          Codex may retry transport requests internally. Error events, timeouts,
          and missing answers stop the run and leave its total unscored. Code
          errors fail checks. Changes to protected files fail all checks for
          that order.
        </p>
        <p>
          Each check gets a fresh QuickJS context: 32 MiB memory, 1 MiB stack,
          and 500 ms CPU time. Source is limited to 24 JavaScript files and 128
          KiB. No host files or network are exposed to the grader.
        </p>
      </section>
      <section>
        <h2>Compare like with like</h2>
        <p>
          The seed fixes generated inputs. Levels increase input sizes; they do
          not change the number of checks. Compare only matching suite hashes,
          seeds, levels, budgets, and runtimes. Use several preselected seeds
          and keep every attempt. Report time and token use separately from
          correctness.
        </p>
        <div className="v2-levels">
          {Object.entries(agentBench.levels).map(([level, size]) => (
            <p key={level}>
              Level {level}: {size.entities} entities, {size.operations}{" "}
              operations as base sizes.
            </p>
          ))}
        </div>
        <p>
          Build cases use one quarter of the operation count, with at least
          eight requests. Policy cases add sentinel records. Fixed boundary
          cases have their own sizes. Exact inputs are saved with each run.
        </p>
      </section>
      <section>
        <h2>What it does not prove</h2>
        <p>
          This tests repairs and requirement changes in small, synthetic
          repositories. It does not test large application design, user
          interfaces, deployment, or long-term agent memory. One run cannot rank
          models.
        </p>
        <p>
          Generators, prompts, and references are public. Evaluation inputs are
          kept outside the task directory, but the local CLI sandbox is not a
          secure hidden-test boundary. Workspace write limits restrict writes;
          they do not fully isolate reads from the host. These results are not
          contamination-proof.
        </p>
        <p>
          Version 2.0 fixes the contract, generators, scoring, and budgets. A
          change to those rules requires a new version. Future versions can add
          harder projects while old results remain reproducible. No fixed test
          suite can promise to stay difficult for ten years.
        </p>
      </section>
      <details className="bench-details">
        <summary>Current suite hash</summary>
        <pre>{agentBench.suite_sha256}</pre>
      </details>
    </article>
  );
}
