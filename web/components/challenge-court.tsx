"use client";
import { useState } from "react";
import Link from "next/link";
import type { CourtChallenge } from "@/lib/bench";

export function ChallengeCourt({
  challenges,
  modelNames,
}: {
  challenges: CourtChallenge[];
  modelNames: string[];
}) {
  const [group, setGroup] = useState("All");
  const groups = ["All", "Build", "Test & debug", "Docs", "Warm-ups"];
  const filtered = challenges.filter(
    (challenge) => group === "All" || challenge.group === group,
  );
  return (
    <div className="challenge-court">
      <div className="court-filters" aria-label="Filter challenges by skill">
        {groups.map((item) => (
          <button
            type="button"
            key={item}
            aria-pressed={group === item}
            onClick={() => setGroup(item)}
          >
            {item}
            <span>
              {
                challenges.filter((c) => item === "All" || c.group === item)
                  .length
              }
            </span>
          </button>
        ))}
        <span className="filter-count" aria-live="polite">
          {filtered.length} challenges
        </span>
      </div>
      <div className="challenge-table-wrap">
        <table className="challenge-table">
          <thead>
            <tr>
              <th scope="col">The challenge / what it tests</th>
              {modelNames.map((name) => (
                <th scope="col" key={name}>
                  {name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((challenge) => (
              <tr
                key={challenge.id}
                className={challenge.lab ? "new-challenge" : ""}
              >
                <th scope="row">
                  <div className="challenge-title-line">
                    <Link href={challenge.href}>
                      {challenge.title}
                      <span aria-hidden="true">↗</span>
                    </Link>
                    {challenge.lab && (
                      <span className="court-tag">New / 1.1</span>
                    )}
                    {challenge.retired && (
                      <span className="retired-tag">Retired warm-up</span>
                    )}
                  </div>
                  <p>{challenge.question}</p>
                  <details>
                    <summary>What the model has to do</summary>
                    <div>
                      {challenge.explains}{" "}
                      <Link href={challenge.href}>
                        Read the full challenge →
                      </Link>
                    </div>
                  </details>
                </th>
                {challenge.scores.map((score) => (
                  <td key={score.model}>
                    <span className="mobile-stat-label">{score.model}</span>
                    <Link
                      href={score.href}
                      aria-label={`${score.model}, ${challenge.title}: ${score.label} ${score.unit}`}
                    >
                      <strong>{score.label}</strong>
                      <small>{score.unit}</small>
                    </Link>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="section-note">
        Original challenges show saved scores out of 10. Counterexample shows
        each attempt out of 8. The three warm-ups are retired; their results
        remain part of the frozen 13-task record.
      </p>
    </div>
  );
}
