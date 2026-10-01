import Link from "next/link";
import { lab } from "@/lib/counterexample";

export function Calibration() {
  if (!lab.calibrationReady)
    return (
      <p className="section-note">
        Calibration is in progress.{" "}
        <Link href="/runs">Inspect the saved attempts</Link>; a comparison will
        appear after repeated runs are complete.
      </p>
    );
  return (
    <>
      <div className="table-scroll">
        <table className="comparison-table">
          <thead>
            <tr>
              <th scope="col">Model</th>
              <th scope="col">Faults exposed / 8</th>
              <th scope="col">Coverage across attempts</th>
              <th scope="col">Runs</th>
            </tr>
          </thead>
          <tbody>
            {lab.models.map((model) => (
              <tr key={model.id}>
                <th scope="row">
                  <div className="model-name">{model.name}</div>
                  <div className="model-detail">
                    Codex CLI · {model.effort} reasoning
                  </div>
                </th>
                <td data-label="Faults exposed / 8">
                  <div className="score-chips">
                    {model.runIds.map((id, index) => {
                      const run = lab.runs.find((item) => item.id === id)!;
                      return (
                        <Link
                          className="score-chip"
                          key={id}
                          href={`/runs/${id}`}
                          aria-label={`${model.name}, attempt ${index + 1}: ${run.score ? `${run.score.killed} of 8 faults` : "unscored"}`}
                        >
                          {run.score ? (
                            <>
                              {run.score.killed}
                              <small>/8</small>
                            </>
                          ) : (
                            "—"
                          )}
                        </Link>
                      );
                    })}
                  </div>
                </td>
                <td data-label="Fault coverage">
                  <div
                    className="mutant-matrix"
                    aria-label={`${model.name} per-fault coverage`}
                  >
                    {lab.faults.map((fault, index) => {
                      const found = model.faultCoverage[fault.id];
                      return (
                        <span
                          key={fault.id}
                          className={`mutant-cell ${found === model.completed ? "found" : found > 0 ? "partial" : ""}`}
                          title={`${fault.name}: exposed in ${found}/${model.completed} completed attempts`}
                        >
                          <span aria-hidden="true">{index + 1}</span>
                          <span className="sr-only">
                            {fault.name}: {found} of {model.completed}{" "}
                            attempts.{" "}
                          </span>
                        </span>
                      );
                    })}
                  </div>
                </td>
                <td
                  data-label="Completed attempts"
                  className="font-mono text-xs"
                >
                  <span>
                    {model.completed}
                    <span className="text-fg-dim"> / {model.attempts}</span>
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="calibration-legend">
        <span>
          <i className="found" />
          Every attempt
        </span>
        <span>
          <i className="partial" />
          Some attempts
        </span>
        <span>
          <i />
          No attempts
        </span>
        <span>Numbers match the eight faults below.</span>
      </div>
      <p className="section-note">
        Three fresh attempts per model, one frozen suite, identical settings.
        Each score links to the complete response. Models are listed
        alphabetically. This is preliminary calibration, not a claim about
        general coding ability.{" "}
        <Link href="/challenges#method">Read the method</Link>.
      </p>
    </>
  );
}
