import Link from "next/link";
import { roster } from "@/lib/bench";
import { lab } from "@/lib/counterexample";
import { Arrow } from "@/components/arrow";

export function ModelRoster() {
  return (
    <div className="roster-board">
      <div className="roster-columns">
        <span>Model / player profile</span>
        <span>
          Original 13 <small>Judged coding score</small>
        </span>
        <span>
          Counterexample Lab <small>Faults exposed, each attempt</small>
        </span>
        <span />
      </div>
      {roster.map((model) => (
        <div
          className="roster-player"
          key={model.id}
          data-player={model.number}
        >
          <Link href={model.href} className="player-identity">
            <span className="jersey-number">{model.number}</span>
            <div>
              <h3>{model.name}</h3>
              <span>OpenAI · ChatGPT subscription</span>
            </div>
          </Link>
          <Link href={`${model.href}#original`} className="player-original">
            <span className="mobile-stat-label">
              Original 13 · judged score
            </span>
            <strong>
              {model.original?.average.toFixed(1) ?? "—"}
              {model.original && <small>/10</small>}
            </strong>
            <span>
              {model.original
                ? `13 challenges · ${model.original.runs ?? 1} run each`
                : "Not run on the original suite"}
            </span>
          </Link>
          <div className="player-new">
            <span className="mobile-stat-label">
              Counterexample · faults exposed
            </span>
            <div className="attempt-strip">
              {model.calibration?.runIds.map((id, index) => {
                const run = lab.runs.find((run) => run.id === id);
                return (
                  <Link
                    key={id}
                    href={`/runs/${id}`}
                    aria-label={`${model.name}, attempt ${index + 1}: ${run?.score?.killed ?? "unscored"} of 8 faults`}
                  >
                    <strong>
                      {run?.score?.killed ?? "—"}
                      <small>/8</small>
                    </strong>
                  </Link>
                );
              }) ?? <span>Not run yet</span>}
            </div>
            <span>
              {model.calibration?.effort ?? "—"} reasoning ·{" "}
              {model.calibration?.failed ? `${model.calibration.failed} unscored · ` : ""}
              preliminary
            </span>
          </div>
          <Link
            className="player-open"
            href={model.href}
            aria-label={`Explore ${model.name}'s full profile`}
          >
            <Arrow diagonal />
          </Link>
        </div>
      ))}
      <div className="roster-caption">
        <span>One model. Two kinds of evidence.</span>
        <Link href="/challenges#scoring">
          How to read the scores <span aria-hidden="true">↗</span>
        </Link>
      </div>
    </div>
  );
}
