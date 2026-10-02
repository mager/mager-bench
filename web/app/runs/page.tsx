import type { Metadata } from "next";
import Link from "next/link";
import { Arrow } from "@/components/arrow";
import { lab, dateLabel, sourceRoot } from "@/lib/counterexample";

export const metadata: Metadata = { title: "Saved runs | mager-bench 1.1" };
export default function Runs() {
  return (
    <div className="site-width">
      <header className="page-header">
        <div className="eyebrow">The paper trail</div>
        <h1>Every attempt is evidence.</h1>
        <p>
          Complete responses and exact scores from Counterexample Lab
          calibration. All {lab.runs.length} saved attempts are here, including
          the weaker ones.
        </p>
      </header>
      <div className="spec-strip">
        <div>
          <strong>{lab.runs.length} attempts</strong>
          <span>{lab.models.length} models</span>
        </div>
        <div>
          <strong>Low reasoning</strong>
          <span>same setting</span>
        </div>
        <div>
          <strong>4,096 tokens</strong>
          <span>prompted target</span>
        </div>
        <div>
          <strong>Subscription</strong>
          <span>Codex CLI</span>
        </div>
      </div>
      <section className="section">
        <div className="section-heading">
          <div>
            <h2>The calibration log</h2>
            <p>
              Ordered by start time. The score is exposed faults out of eight.
            </p>
          </div>
          <a
            className="text-link"
            href={`${sourceRoot}/blob/main/runs/v1.1/2026-10-01-calibration.md`}
          >
            Latest run protocol
            <Arrow diagonal />
          </a>
        </div>
        <div className="run-list">
          {[...lab.runs]
            .sort((a, b) => a.generated_at.localeCompare(b.generated_at))
            .map((run) => (
              <Link className="run-row" href={`/runs/${run.id}`} key={run.id}>
                <div>
                  <strong className="model-name">{run.modelName}</strong>
                  <p className="model-detail">
                    Attempt {run.id.match(/r(\d+)$/)?.[1]} ·{" "}
                    {run.reasoning_effort} reasoning · {run.status}
                  </p>
                </div>
                <span className="run-date text-xs text-fg-dim">
                  {dateLabel(run.generated_at)}
                </span>
                <span className="font-mono text-sm">
                  {run.score ? `${run.score.killed} / 8` : "Unscored"}
                </span>
                <Arrow />
              </Link>
            ))}
        </div>
        <p className="section-note">
          The September 30 calibration resumed after an interruption; its{" "}
          <a
            href={`${sourceRoot}/blob/main/runs/v1.1/2026-09-30-calibration.md`}
          >
            original protocol
          </a>{" "}
          retains that execution note. The October 1 protocol records the new
          subjects and availability checks. No missing output is assigned a
          score.
        </p>
      </section>
      <div className="archive-teaser">
        <div>
          <h2>One frozen suite.</h2>
          <p>
            All displayed results are regraded by the exporter before
            publication. The suite fingerprint must match.
          </p>
          <p className="break-all font-mono text-[10px]">{lab.suiteHash}</p>
        </div>
        <a className="button-secondary" href="/api/v1.1/results">
          Get the JSON
          <Arrow />
        </a>
      </div>
    </div>
  );
}
