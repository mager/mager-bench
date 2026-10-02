"use client";
import { useState } from "react";
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

export function EverydayExplorer({ tasks }: { tasks: Task[] }) {
  const [selected, setSelected] = useState(0);
  const [caseIndex, setCaseIndex] = useState(0);
  const task = tasks[selected],
    example = task.cases[caseIndex];
  return (
    <section
      className="everyday-section"
      id="tasks"
      aria-labelledby="tasks-heading"
    >
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
      <div className="example-heading">
        <h3>{task.title}</h3>
        <p>{describe(task.id, example.input, task.description)}</p>
      </div>
      <div className="case-control">
        <label htmlFor="case">Explore a test case</label>
        <select
          id="case"
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
        <span>Expected result</span>
        <p>{readable(task.id, example.expected)}</p>
      </div>
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
      <p className="quiet">
        These are the published test cases, not a model’s answers. Saved
        attempts show what the model actually returned.
      </p>
      <details className="bench-details">
        <summary>Read the exact prompt</summary>
        <pre className="prose-code">{task.prompt}</pre>
      </details>
    </section>
  );
}
