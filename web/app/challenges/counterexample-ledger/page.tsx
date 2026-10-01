import type { Metadata } from "next";
import Link from "next/link";
import { LabDemo } from "@/components/lab-demo";
import { Arrow } from "@/components/arrow";
import { lab, sourceRoot } from "@/lib/counterexample";

export const metadata: Metadata = {
  title: "Counterexample Lab explained | mager-bench 1.1",
  description:
    "Design twelve events that expose eight faulty ledgers. Read the complete Counterexample Lab contract and scoring method.",
};

export default function Challenge() {
  return (
    <div className="site-width">
      <header className="page-header">
        <div className="eyebrow">The new challenge / 1.1</div>
        <h1>Can it find the bug?</h1>
        <p>
          The original challenges ask a model to build something. This one asks
          it to design tests that catch broken code. A ledger is just a record
          of account balances and transfers. We give the model its rules and
          ask: which short sequence of actions would reveal a mistake?
        </p>
      </header>
      <section className="method-grid section pt-0" id="walkthrough">
        <div>
          <h2 className="section-title">Here’s how one attempt works.</h2>
          <ol className="method-steps">
            <li>
              <div>
                <strong>Read the contract.</strong>Every trace starts with A =
                10, B = 0, C = 0, zero revisions, and an empty request cache.
              </div>
            </li>
            <li>
              <div>
                <strong>Write tests, with exact expectations.</strong>Submit
                JSON containing one to four independent traces. Transfer,
                inspect, and restart all cost one event. The total budget is
                twelve events.
              </div>
            </li>
            <li>
              <div>
                <strong>Get the correct ledger right.</strong>Every expectation
                in a trace must agree with the reference implementation. One
                wrong expectation invalidates that entire trace’s coverage.
              </div>
            </li>
            <li>
              <div>
                <strong>Make faulty ledgers disagree.</strong>A valid trace
                exposes a faulty implementation if any output differs. Each of
                the eight faults counts once, however many tests catch it.
              </div>
            </li>
          </ol>
          <p className="section-note">
            A “counterexample” is an input that proves an implementation is
            wrong. In the walkthrough, both versions reject a bad transfer, but
            one still removes money. Checking the balance exposes the mistake.
            Replay the atomicity example below. It is hand-authored, not a model
            submission.
          </p>
        </div>
        <LabDemo demos={lab.demos} initialDemoId="atomicity" />
      </section>
      <section className="section">
        <div className="court-section-heading">
          <div>
            <span className="eyebrow">Read a result</span>
            <h2>What does 7 out of 8 mean?</h2>
          </div>
        </div>
        <div className="scoring-pair prose-copy">
          <div>
            <p>
              The submitted tests exposed{" "}
              <strong>seven distinct faulty versions</strong> of the ledger.
              Catching the same fault ten times still counts once. A missed
              fault can survive because the model never chose the right event,
              or because it failed to check the output that would reveal it.
            </p>
            <p>
              Each trace starts fresh with A = 10, B = 0, and C = 0. A trace is
              a sequence of actions, each paired with its expected result. If
              one expectation is wrong, that whole trace earns no coverage.
            </p>
          </div>
          <div>
            <p>
              Astra exposed <strong>7/8, 7/8, 7/8</strong>; Sol exposed{" "}
              <strong>7/8, 6/8, 5/8</strong> in the first calibration. All
              submitted traces had correct expectations. Neither model caught
              the partial-transfer fault.
            </p>
            <p>
              Those are three separate attempts per model, all at low reasoning
              effort. They measure test design on this specific contract. They
              are not percentages or a replacement for the original coding
              average.
            </p>
            <Link className="text-link mt-4" href="/#models">
              See both model profiles
              <Arrow />
            </Link>
          </div>
        </div>
      </section>
      <section className="section" id="faults">
        <div className="court-section-heading">
          <div>
            <span className="eyebrow">The fault list</span>
            <h2>Eight ways the ledger can be wrong.</h2>
          </div>
        </div>
        <p className="court-section-intro">
          Each faulty version changes one behavior. The model sees the contract,
          not this list of faults. Its tests have to distinguish the correct
          implementation from these broken ones.
        </p>
        <ol className="fault-list">
          {lab.faults.map((fault, index) => (
            <li className="fault-item" key={fault.id}>
              <span className="fault-number">0{index + 1}</span>
              <div>
                <h3>{fault.name}</h3>
                <p>{fault.description}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>
      <section className="section" id="contract">
        <div className="section-heading">
          <div>
            <div className="eyebrow">What the model sees</div>
            <h2>The exact prompt</h2>
            <p>
              Read the complete rules, including validation order, ID conflicts,
              and durable request history.
            </p>
          </div>
          <a
            className="text-link"
            href={`${sourceRoot}/blob/main/counterexample_lab/prompt.md`}
          >
            View source
            <Arrow diagonal />
          </a>
        </div>
        <details className="details-panel">
          <summary>Open the complete model prompt</summary>
          <pre className="code-panel whitespace-pre-wrap">{lab.prompt}</pre>
        </details>
      </section>
      <section className="section" id="method">
        <div className="section-heading">
          <div>
            <div className="eyebrow">Methodology</div>
            <h2>A measurement you can reproduce.</h2>
          </div>
        </div>
        <div className="method-grid prose-copy">
          <div>
            <p>
              <strong>No LLM judge.</strong> The Python oracle checks exact
              output objects. Eight separate faulty implementations run the same
              submitted events. Code computes coverage; prose and presentation
              earn no points.
            </p>
            <p>
              <strong>Same conditions.</strong> This calibration used three
              fresh Codex CLI calls each for GPT-6 Astra and GPT-5.6 Sol,
              interleaved at low reasoning effort with a 4,096-token output
              target. Both used the local ChatGPT subscription. The token target
              is an instruction, not an API-enforced cap.
            </p>
            <p>
              <strong>Every saved attempt.</strong> Responses, timing, settings,
              and reproducible scores are published. Empty, malformed, and
              provider failures are unscored, never zero. An execution
              interruption during calibration is documented in the{" "}
              <a
                href={`${sourceRoot}/blob/main/runs/v1.1/2026-09-30-calibration.md`}
              >
                run protocol
              </a>
              .
            </p>
          </div>
          <div>
            <p>
              <strong>A narrow test.</strong> Three runs per model are
              preliminary evidence, not a statistically established ranking. The
              fixed, public fault corpus can become familiar. This measures test
              design for one small stateful contract, not general coding
              ability.
            </p>
            <p>
              <strong>Keep versions separate.</strong> The old board measures
              LLM-judged coding submissions on a 0–10 scale. Version 1.1
              measures exposed faults out of eight. A substantive change to this
              contract, fault corpus, budget, or scoring becomes 1.2.
            </p>
            <p>
              <strong>What comes next.</strong> More models and repeated runs
              should probe the ceiling. Astra missed the partial-transfer fault
              in all three attempts. That’s a useful blind spot to study before
              designing the next version.
            </p>
          </div>
        </div>
        <p className="section-note break-all font-mono">
          Frozen suite SHA-256: {lab.suiteHash}
        </p>
      </section>
      <section className="archive-teaser">
        <div>
          <h2>Run it. Inspect it. Try to break it.</h2>
          <p>
            The prompt, oracle, faulty ledgers, and saved attempts are public.
          </p>
        </div>
        <Link className="button-primary" href="/runs">
          Explore the runs
          <Arrow />
        </Link>
      </section>
    </div>
  );
}
