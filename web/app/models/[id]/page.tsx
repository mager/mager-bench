import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { roster, challengeNotes, originalBoard } from "@/lib/bench";
import { lab, dateLabel } from "@/lib/counterexample";
import { modelHref } from "@/lib/model-path";
import { Arrow } from "@/components/arrow";

type Props = { params: Promise<{ id: string }> };
export function generateStaticParams() {
  return roster.map((model) => ({ id: model.slug }));
}
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const model = roster.find((m) => m.slug === id);
  return {
    title: model
      ? `${model.name} | Player profile | mager-bench`
      : "Model not found",
    description: model
      ? `${model.name}'s saved benchmark results, Counterexample Lab attempts, and the evidence behind each result.`
      : undefined,
  };
}
export default async function ModelPage({ params }: Props) {
  const { id } = await params;
  const model = roster.find((m) => m.slug === id);
  if (!model) notFound();
  const calibration = model.calibration;
  const original = model.original;
  const attempts = lab.runs.filter((run) => run.model === model.id);
  const weakest = [...model.challenges].sort((a, b) => a.total - b.total)[0];
  return (
    <div className="site-width">
      <header className="page-header" data-player={model.number}>
        <Link className="text-link mb-7" href="/#models">
          ← The lineup
        </Link>
        <div className="profile-hero">
          <div>
            <div className="eyebrow">Player profile / OpenAI</div>
            <h1>{model.name}</h1>
            <p className="prose-copy">
              ChatGPT subscription · Codex CLI
              <br />
              {model.challenges.length} original challenges. {attempts.length}{" "}
              Counterexample attempts. Every answer on the record.
            </p>
          </div>
          <span className="profile-jersey" aria-hidden="true">
            {model.number}
          </span>
        </div>
      </header>
      <div className="profile-scores">
        <div>
          <div className="eyebrow">Original 13 / Historical coding results</div>
          {original ? (
            <>
              <h2>
                {original.average.toFixed(1)}{" "}
                <span className="text-fg-dim text-xl">out of 10</span>
              </h2>
              <p>
                Mean across thirteen tasks, scored by GPT-5.6 Sol.{" "}
                {original.runs ?? 1} run per task,{" "}
                {dateLabel(originalBoard.generated_at)}.
              </p>
              <div className="profile-dimensions">
                <div>
                  Correctness
                  <strong>{original.avg_correctness.toFixed(1)}</strong>
                </div>
                <div>
                  Code quality<strong>{original.avg_quality.toFixed(1)}</strong>
                </div>
                <div>
                  Documentation
                  <strong>{original.avg_documentation.toFixed(1)}</strong>
                </div>
              </div>
            </>
          ) : (
            <>
              <h2>Not run.</h2>
              <p>This model has only been tested on Counterexample Lab 1.1.</p>
            </>
          )}
        </div>
        <div>
          <div className="eyebrow">Counterexample Lab / Version 1.1</div>
          <h2>
            {calibration
              ? `${attempts.length} attempts. Every result.`
              : "Waiting for a run."}
          </h2>
          <div className="profile-lab-attempts">
            {attempts.map((run, index) => (
              <Link href={`/runs/${run.id}`} key={run.id}>
                <span>Attempt {index + 1}</span>
                <strong>
                  {run.score ? `${run.score.killed}/8` : "Unscored"}
                </strong>
              </Link>
            ))}
          </div>
          <p>
            {calibration?.effort ?? "—"} reasoning · faulty versions exposed ·
            preliminary calibration
          </p>
        </div>
      </div>
      {original && weakest ? (
        <section className="section" id="original">
          <div className="section-heading">
            <div>
              <span className="eyebrow">Original 13</span>
              <h2>The full box score</h2>
              <p>
                Highest to lowest. The lowest score here is{" "}
                {challengeNotes[weakest.name].title.toLowerCase()} at{" "}
                {weakest.total.toFixed(1)}/10. Open any task to inspect the
                submission and the judge’s notes.
              </p>
            </div>
            <Link className="text-link" href="/challenges#scoring">
              Scoring rules
              <Arrow />
            </Link>
          </div>
          <div className="profile-task-list">
            {[...model.challenges]
              .sort((a, b) => b.total - a.total)
              .map((challenge) => (
                <Link
                  className="profile-task"
                  href={modelHref(model.id, challenge.name)}
                  key={challenge.name}
                >
                  <div>
                    <h3>{challengeNotes[challenge.name].title}</h3>
                    <p>{challengeNotes[challenge.name].question}</p>
                  </div>
                  <meter
                    min="0"
                    max="10"
                    value={challenge.total}
                    aria-label={`${challengeNotes[challenge.name].title} score`}
                  />
                  <span>
                    {challenge.total.toFixed(1)}
                    <small> /10</small>
                  </span>
                  <Arrow />
                </Link>
              ))}
          </div>
          <p className="section-note">
            These scores are preserved from the original suite, including three
            retired warm-ups. They are not a new run. The model-judge setup,
            single samples, and self-judging for Sol limit how much to read into
            small differences.
          </p>
        </section>
      ) : (
        <section className="section" id="original">
          <h2>No original-suite results</h2>
          <p className="section-note">
            No historical coding score is assigned to this model. Its saved
            evidence is the Counterexample Lab attempts below.
          </p>
        </section>
      )}
      <section className="section" id="counterexample">
        <div className="section-heading">
          <div>
            <span className="eyebrow">New challenge / 1.1</span>
            <h2>What did its tests actually catch?</h2>
            <p>
              A model must predict the correct ledger’s outputs exactly before
              its tests can earn credit for exposing a fault. These counts show
              how often {model.name} caught each fault.
            </p>
          </div>
          <Link className="text-link" href="/challenges/counterexample-ledger">
            Understand the test
            <Arrow />
          </Link>
        </div>
        <ul className="fault-status-list">
          {lab.faults.map((fault, index) => (
            <li key={fault.id}>
              <div>
                <span className="mr-3 text-fg-dim">0{index + 1}</span>
                {fault.name}
              </div>
              <span
                className={
                  calibration?.faultCoverage[fault.id]
                    ? "text-green"
                    : "text-fg-dim"
                }
              >
                {calibration
                  ? `${calibration.faultCoverage[fault.id]} / ${calibration.completed} attempts`
                  : "Not run"}
              </span>
            </li>
          ))}
        </ul>
        <div className="run-list mt-6">
          {attempts.map((run, index) => (
            <Link className="run-row" href={`/runs/${run.id}`} key={run.id}>
              <div>
                <strong className="model-name">Attempt {index + 1}</strong>
                <p className="model-detail">
                  {run.reasoning_effort} reasoning ·{" "}
                  {run.score?.events_used ?? "—"} events
                </p>
              </div>
              <span className="run-date text-xs text-fg-dim">
                {dateLabel(run.generated_at)}
              </span>
              <span className="font-mono text-sm">
                {run.score ? `${run.score.killed} / 8 faults` : "Unscored"}
              </span>
              <Arrow />
            </Link>
          ))}
        </div>
        <p className="section-note">
          Same frozen contract and settings across all attempts.{" "}
          {attempts.reduce(
            (sum, run) => sum + (run.score?.valid_traces ?? 0),
            0,
          )}{" "}
          of{" "}
          {attempts.reduce(
            (sum, run) => sum + (run.score?.total_traces ?? 0),
            0,
          )}{" "}
          graded traces matched the reference. All responses are preserved,
          including weaker attempts and unscored failures.
        </p>
      </section>
      <div className="archive-teaser">
        <Link className="text-link" href="/#models">
          Compare the lineup
          <Arrow />
        </Link>
        <Link className="text-link" href="/challenges">
          Explore the challenges
          <Arrow />
        </Link>
      </div>
    </div>
  );
}
