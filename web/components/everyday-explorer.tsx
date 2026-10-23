"use client";
import { useId, useState } from "react";
import type { Task } from "@/lib/everyday";

function describe(id: string, input: unknown, fallback: string): string {
  if (id !== "split-bill") return fallback;
  const data = input as {
    expenses: {
      paidBy: string;
      cents: number;
      shares: { person: string; weight: number }[];
    }[];
  };
  return (
    data.expenses
      .map(
        (e) =>
          `${e.paidBy} ${e.cents < 0 ? "received a refund of" : "paid"} $${(Math.abs(e.cents) / 100).toFixed(2)}, split between ${e.shares.map((s) => `${s.person} (${s.weight} share${s.weight === 1 ? "" : "s"})`).join(", ")}.`,
      )
      .join(" ") || "No shared expenses."
  );
}

function readable(id: string, output: unknown): string {
  if (id === "build-plan") {
    const result = output as {
      error?: string;
      order: string[];
      finish: number;
      criticalPath: string[];
    };
    if (result.error)
      return "A required dependency cycle makes this build impossible.";
    if (!result.order.length)
      return "No targets requested. Nothing needs to run.";
    const path = result.criticalPath;
    return `Finish in ${result.finish} time units. Critical path: ${path.length > 8 ? `${path.slice(0, 3).join(" → ")} → … → ${path.at(-1)} (${path.length} jobs)` : path.join(" → ")}.`;
  }
  if (id === "job-selection") {
    const result = output as { ids: string[]; profit: number; cost: number };
    if (!result.ids.length)
      return "Choose no jobs. Profit and cost are both zero.";
    const names =
      result.ids.length > 8
        ? `${result.ids.length} jobs (see the exact list below)`
        : result.ids.join(", ");
    return `Choose ${names}. Total profit: ${result.profit}. Total cost: ${result.cost}.`;
  }
  if (id === "split-bill") {
    const result = output as {
      transfers: { from: string; to: string; cents: number }[];
    };
    return result.transfers.length
      ? result.transfers
          .map((t) => `${t.from} pays ${t.to} $${(t.cents / 100).toFixed(2)}.`)
          .join(" ")
      : "Everyone is settled. No payments needed.";
  }
  if (id === "clean-csv") {
    const result = output as {
      contacts: { name: string; email: string }[];
      rejected: number;
    };
    return `${result.contacts.length} contact${result.contacts.length === 1 ? "" : "s"} kept. ${result.rejected} row${result.rejected === 1 ? "" : "s"} rejected. ${result.contacts.map((c) => `${c.name} (${c.email})`).join("; ")}`;
  }
  if (!output) return "There is no meeting time that works for everyone.";
  const result = output as { start: number; end: number };
  const clock = (n: number) =>
    `${n >= 1440 ? "day 2, " : ""}${String(Math.floor(n / 60) % 24).padStart(2, "0")}:${String(n % 60).padStart(2, "0")}`;
  return `Meet from ${clock(result.start)} to ${clock(result.end)} UTC.`;
}

export function EverydayExplorer({
  tasks,
  compact = false,
}: {
  tasks: Task[];
  compact?: boolean;
}) {
  const caseId = useId();
  const [selected, setSelected] = useState(0);
  const [caseIndex, setCaseIndex] = useState(0);
  const task = tasks[selected],
    example = task.cases[caseIndex];
  const caseColumns = (
    <div className="case-columns">
      <div>
        <h4>Input</h4>
        <pre tabIndex={0} aria-label="Test input">
          {JSON.stringify(example.input, null, 2)}
        </pre>
      </div>
      <div>
        <h4>Exact expected output</h4>
        <pre tabIndex={0} aria-label="Expected output">
          {JSON.stringify(example.expected, null, 2)}
        </pre>
      </div>
    </div>
  );
  return (
    <section
      className={compact ? "task-example" : "everyday-section"}
      id={compact ? undefined : "tasks"}
      aria-labelledby={compact ? undefined : "tasks-heading"}
      aria-label={compact ? task.title : undefined}
    >
      {!compact && (
        <>
          <div className="bench-section-title">
            <h2 id="tasks-heading">What we ask it to build</h2>
            <span>12 checks per program</span>
          </div>
          <div className="task-selector" role="group" aria-label="Choose a program">
            {tasks.map((t, i) => (
              <button
                type="button"
                key={t.id}
                aria-pressed={selected === i}
                onClick={() => {
                  setSelected(i);
                  setCaseIndex(0);
                }}
              >
                <span>{t.title}</span>
                <span className="task-description">{t.description}</span>
              </button>
            ))}
          </div>
        </>
      )}
      {(!compact || task.id === "split-bill") && (
        <div className="example-heading">
          {!compact && <h3>{task.title}</h3>}
          <p>{describe(task.id, example.input, task.description)}</p>
        </div>
      )}
      <div className="case-control">
        <label htmlFor={caseId}>
          {compact ? "Test case" : "Explore a test case"}
        </label>
        <select
          id={caseId}
          value={caseIndex}
          onChange={(e) => setCaseIndex(Number(e.target.value))}
        >
          {task.cases.map((c, i) => (
            <option value={i} key={c.label}>
              {c.label}
            </option>
          ))}
        </select>
      </div>
      <div className="expected-answer" aria-live="polite">
        <span>
          {compact ? "Expected answer · published test data" : "Expected result"}
        </span>
        <p>{readable(task.id, example.expected)}</p>
      </div>
      {compact ? (
        <details className="bench-details">
          <summary>Input and expected JSON</summary>
          {caseColumns}
        </details>
      ) : caseColumns}
      {!compact && (
        <p className="quiet">
          These are the published test cases, not a model’s answers. Saved
          attempts show what the model actually returned.
        </p>
      )}
      <details className="bench-details">
        <summary>{compact ? "Exact prompt" : "Read the exact prompt"}</summary>
        <pre className="prose-code">{task.prompt}</pre>
      </details>
    </section>
  );
}
