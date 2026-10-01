import type { Metadata } from "next";
import Link from "next/link";
import { LabDemo } from "@/components/lab-demo";
import { Arrow } from "@/components/arrow";
import { lab, sourceRoot } from "@/lib/counterexample";

export const metadata: Metadata = {
  title: "The challenge | mager-bench 1.1",
  description:
    "Design twelve events that expose eight faulty ledgers. Read the complete Counterexample Lab contract and scoring method.",
};

export default function Challenge() {
  return (
    <div className="site-width">
      <header className="page-header">
        <div className="eyebrow">The active challenge / 1.1</div>
        <h1>A good test finds the exception.</h1>
        <p>
          Build a small regression suite for a ledger that moves money between
          three accounts. Cover what happens when requests repeat, fail,
          conflict, or survive a restart.
        </p>
      </header>
      <section className="method-grid section pt-0">
        <div>
          <h2 className="section-title">Twelve events. Make them count.</h2>
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
            The model receives the contract and no fault-specific hints. The
            walkthrough here is a hand-authored explanation, not a model
            submission.
          </p>
        </div>
        <LabDemo demos={lab.demos} />
      </section>
      <section className="section" id="contract">
        <div className="section-heading">
          <div>
            <div className="eyebrow">The source of truth</div>
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
