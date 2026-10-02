import Link from "next/link";
import { Arrow } from "@/components/arrow";
import { CourtMark } from "@/components/court-mark";
import { ModelRoster } from "@/components/model-roster";
import { ChallengeCourt } from "@/components/challenge-court";
import { courtChallenges, roster } from "@/lib/bench";

export default function Home() {
  return (
    <div className="site-width court-home">
      <section className="court-hero">
        <div className="court-hero-copy">
          <div className="eyebrow">
            <span className="court-dot" />A pickup game for coding models
          </div>
          <h1>
            Who’s got <span>next?</span>
          </h1>
          <p>
            Same court. Same challenges. See how each model plays, from a simple
            function to a whole game, then put its testing instincts under
            pressure.
          </p>
          <a className="court-hero-link" href="#models">
            Meet the lineup <Arrow />
          </a>
        </div>
        <div className="hero-court">
          <CourtMark />
          <div className="court-stamp">
            <strong>
              MAGER
              <br />
              BENCH
            </strong>
            <span>OPEN COURT / EST. 2026</span>
          </div>
          <span className="court-side-note">
            BRING YOUR MODEL. SHOW YOUR WORK.
          </span>
        </div>
      </section>
      <section id="models" className="lineup-section">
        <div className="court-section-heading">
          <div>
            <span className="eyebrow">On the court</span>
            <h2>
              The lineup
              <span className="heading-count">{roster.length} models</span>
            </h2>
          </div>
          <Link className="text-link" href="/runs">
            Every new attempt
            <Arrow />
          </Link>
        </div>
        <ModelRoster />
        <p className="roster-explanation">
          The 9.3 and 9.0 are the original coding averages. The new test counts
          broken implementations caught out of eight. Both belong on the model’s
          record, with their own scoring rules.
        </p>
      </section>
      <section className="court-section" id="challenges">
        <div className="court-section-heading">
          <div>
            <span className="eyebrow">Know their game</span>
            <h2>Every challenge. Every model.</h2>
          </div>
          <Link className="text-link" href="/challenges">
            The full playbook
            <Arrow />
          </Link>
        </div>
        <p className="court-section-intro">
          Thirteen original challenges test what a model can build, explain, and
          fix. Counterexample Lab adds a different question: can it write the
          tests that catch someone else’s mistakes?
        </p>
        <ChallengeCourt
          challenges={courtChallenges}
          modelNames={roster.map((model) => model.name)}
        />
      </section>
      <section className="counterexample-feature">
        <div className="counterexample-feature-copy">
          <span className="court-tag">The new challenge / 1.1</span>
          <h2>
            Good code is one thing.
            <br />
            <span>Catching bad code is another.</span>
          </h2>
          <p>
            Give a model the rules for a tiny money-transfer system. Ask it to
            write tests. Then run those tests against eight broken versions. It
            only gets credit when it knows the correct answer and exposes a bug.
          </p>
          <Link
            className="button-primary"
            href="/challenges/counterexample-ledger"
          >
            See exactly how it works
            <Arrow />
          </Link>
        </div>
        <div className="counterexample-play">
          <div className="play-caption">A BUG THE FIRST TWO MODELS MISSED</div>
          <div className="play-event">
            <span>01</span>
            <p>Send 3 to an account that doesn’t exist.</p>
          </div>
          <div className="play-event">
            <span>02</span>
            <p>The transfer fails. Check your balance.</p>
          </div>
          <div className="play-outcomes">
            <div>
              <span>Should be</span>
              <strong>10</strong>
            </div>
            <div>
              <span>Broken version</span>
              <strong>7</strong>
            </div>
          </div>
          <p>The error looks right. The missing money gives it away.</p>
          <Link href="/challenges/counterexample-ledger#walkthrough">
            Replay this counterexample <Arrow />
          </Link>
        </div>
      </section>
      <div className="court-bottom">
        <p>Built by Mager. Small sample, open evidence, room to get better.</p>
        <Link className="text-link" href="/archive">
          Earlier boards & judges
          <Arrow />
        </Link>
      </div>
    </div>
  );
}
