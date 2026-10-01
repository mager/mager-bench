import Link from "next/link";
import { Arrow } from "@/components/arrow";
import { LabDemo } from "@/components/lab-demo";
import { Calibration } from "@/components/calibration";
import { lab, dateLabel } from "@/lib/counterexample";

export default function Home() {
  return (
    <div className="site-width">
      <section className="hero">
        <div>
          <div className="eyebrow">
            <span className="rule" />
            The Counterexample Lab
          </div>
          <h1>
            Make the model
            <br />
            <span>find the bug.</span>
          </h1>
          <p className="hero-description">
            Writing code is one test. Knowing how it breaks is another. Eight
            faulty ledgers. Twelve events. Can a model design the tests that
            catch them?
          </p>
          <div className="hero-actions">
            <Link className="button-primary" href="/challenges">
              Explore the challenge
              <Arrow />
            </Link>
            <a className="button-secondary" href="#calibration">
              See the results
              <Arrow />
            </a>
          </div>
          <p className="hero-footnote">
            mager-bench 1.1 · deterministic scoring · open source
          </p>
        </div>
        <LabDemo demos={lab.demos} />
      </section>
      <div className="spec-strip">
        <div>
          <strong>12 events</strong>
          <span>total test budget</span>
        </div>
        <div>
          <strong>8 faults</strong>
          <span>one fixed corpus</span>
        </div>
        <div>
          <strong>0 judges</strong>
          <span>checked by code</span>
        </div>
        <div>
          <strong>Every attempt</strong>
          <span>open for inspection</span>
        </div>
      </div>
      <section className="section" id="calibration">
        <div className="section-heading">
          <div>
            <div className="eyebrow">01 / The evidence</div>
            <h2>First calibration. All the attempts.</h2>
            <p>
              A score counts faulty implementations exposed by a model’s tests.
              The expected outputs must be right, too.
            </p>
          </div>
          <span className="status-pill">
            <span className="status-dot" />
            {lab.calibrationReady
              ? "Preliminary results"
              : "Calibration in progress"}
          </span>
        </div>
        <Calibration />
        <div className="section-end">
          <span>
            {lab.lastRunAt ? dateLabel(lab.lastRunAt) : "No completed runs"} ·
            ChatGPT subscription · no API calls
          </span>
          <Link className="text-link" href="/runs">
            Inspect all {lab.runs.length} attempts
            <Arrow />
          </Link>
        </div>
      </section>
      <section className="section fault-section" id="faults">
        <div className="fault-intro">
          <div className="eyebrow">02 / The fault line-up</div>
          <h2 className="section-title">
            Small mistakes.
            <br />
            Interesting consequences.
          </h2>
          <p>
            Each faulty ledger changes one behavior. The challenge is finding a
            short sequence of events that makes that mistake visible.
          </p>
          <Link className="text-link" href="/challenges#contract">
            Read the exact contract
            <Arrow />
          </Link>
        </div>
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
      <aside className="archive-teaser">
        <div>
          <span className="eyebrow">
            A new chapter, a different measurement
          </span>
          <h2>Looking for the old leaderboard?</h2>
          <p>
            The 9.0 and 9.3 averages belong to the original thirteen-task,
            LLM-judged suite. Those results are preserved in the archive. They
            are not Counterexample Lab scores.
          </p>
        </div>
        <Link className="button-secondary" href="/archive">
          Open the archive
          <Arrow />
        </Link>
      </aside>
    </div>
  );
}
