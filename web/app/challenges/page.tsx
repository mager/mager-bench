import type { Metadata } from "next";
import Link from "next/link";
import { ChallengeCourt } from "@/components/challenge-court";
import { courtChallenges, roster, originalBoard } from "@/lib/bench";
import { Arrow } from "@/components/arrow";
import { dateLabel } from "@/lib/counterexample";
export const metadata: Metadata = {
  title: "The challenges | mager-bench",
  description:
    "Understand all thirteen original coding challenges and Counterexample Lab. Compare models, inspect their answers, and see exactly how each score works.",
};
export default function Challenges() {
  return (
    <div className="site-width">
      <header className="page-header">
        <div className="eyebrow">The playbook</div>
        <h1>
          Different skills.
          <br />
          Same court.
        </h1>
        <p>
          A model’s average only tells part of the story. These tasks test
          implementation, debugging, documentation, language conventions, and
          complete applications. Open a score to see the answer behind it.
        </p>
      </header>
      <ChallengeCourt
        challenges={courtChallenges}
        modelNames={roster.map((model) => model.name)}
      />
      <section className="section" id="scoring">
        <div className="court-section-heading">
          <div>
            <span className="eyebrow">Read the scoreboard</span>
            <h2>Two tests. Two scoring systems.</h2>
          </div>
        </div>
        <div className="scoring-pair">
          <div>
            <span className="score-unit">ORIGINAL 13 / SCORES OUT OF 10</span>
            <h3>How well did it do the job?</h3>
            <div className="prose-copy">
              <p>
                The model writes a solution to each prompt. GPT-5.6 Sol judges{" "}
                <strong>correctness, code quality, and documentation</strong>{" "}
                against that challenge’s rubric.
              </p>
              <p>
                The task score is the mean of those three dimensions, rounded to
                one decimal. The model’s overall coding average summarizes all
                thirteen task scores. Speed is reported separately.
              </p>
            </div>
            <p className="score-formula">
              Task score = (correctness + quality + docs) ÷ 3
            </p>
            <div className="prose-copy">
              <p>
                This board is a <strong>frozen historical record</strong> from{" "}
                {dateLabel(originalBoard.generated_at)}, with one saved run per
                task. Small gaps are weak evidence: an LLM judge can make
                mistakes, and Sol also judges its own answers.
              </p>
              <p>
                FizzBuzz, binary search, and refactor are retired warm-ups. The
                other ten remain optional baselines; all original prompts and
                scores stay available.
              </p>
            </div>
          </div>
          <div>
            <span className="score-unit">
              COUNTEREXAMPLE LAB / FAULTS OUT OF 8
            </span>
            <h3>Can it catch a wrong implementation?</h3>
            <div className="prose-copy">
              <p>
                The model designs tests for a tiny ledger. Each test says what
                to do and <strong>exactly what should happen</strong>. A correct
                reference implementation checks those expectations.
              </p>
              <p>
                Then the same tests run against eight faulty ledgers. Each
                distinct faulty version exposed by a valid trace earns one
                point. Code computes the result; there is no LLM judge.
              </p>
            </div>
            <p className="score-formula">
              Result = distinct faulty versions exposed / 8
            </p>
            <div className="prose-copy">
              <p>
                Version 1.1 limits each submission to twelve events across at
                most four traces. A trace with one wrong expectation earns no
                coverage. Malformed or failed calls are unscored.
              </p>
              <p>
                The first calibration used three independent attempts per model
                at low reasoning effort. We show every attempt. These are
                preliminary results on a narrow test.
              </p>
            </div>
            <Link
              className="text-link mt-5"
              href="/challenges/counterexample-ledger"
            >
              Walk through a counterexample
              <Arrow />
            </Link>
          </div>
        </div>
        <p className="section-note">
          The coding averages and fault counts measure different things. They
          stay separate on every model’s profile. Changing the Counterexample
          contract, faults, budget, or scoring will create version 1.2.
        </p>
      </section>
      <div className="archive-teaser">
        <div>
          <h2>Start with a model. Follow the evidence.</h2>
          <p>
            Each profile connects the results to the original responses,
            prompts, and scoring notes.
          </p>
        </div>
        <Link className="button-primary" href="/#models">
          Back to the lineup
          <Arrow />
        </Link>
      </div>
    </div>
  );
}
