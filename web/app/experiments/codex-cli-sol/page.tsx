import type { Metadata } from "next";
import Link from "next/link";
import experimentData from "@/data/codex-cli-sol.json";
import challengeDefs from "@/data/challenges.json";

export const metadata: Metadata = {
  title: "GPT-5.6 Sol via Codex CLI — mager-bench",
  description: "An inspectable 13-challenge Codex CLI run on the ChatGPT subscription leaderboard.",
};

type Row = (typeof experimentData.rows)[number];

function scoreColor(score: number) {
  if (score > 9.5) return "text-green";
  if (score >= 7) return "text-amber";
  return "text-alert";
}

const descriptions = new Map(challengeDefs.map((item) => [item.name, item.description]));
const rows = [...experimentData.rows].sort((a, b) => b.total - a.total);

function ScoreBreakdown({ row }: { row: Row }) {
  return (
    <div className="flex flex-wrap gap-x-5 gap-y-1 text-xs text-fg-dim">
      <span>correctness <strong className="text-green">{row.correctness.toFixed(1)}</strong></span>
      <span>quality <strong className="text-magenta">{row.quality.toFixed(1)}</strong></span>
      <span>docs <strong className="text-cyan">{row.documentation.toFixed(1)}</strong></span>
      <span>{(row.speed_ms / 1000).toFixed(1)}s generation</span>
    </div>
  );
}

export default function CodexCLIExperiment() {
  return (
    <main className="px-4 py-10 sm:px-8 md:py-16">
      <div className="mx-auto flex max-w-4xl flex-col gap-9">
        <header className="border-b border-amber-faint pb-6">
          <Link href="/" className="text-xs text-fg-dim hover:text-amber-bright">
            ← mager-bench
          </Link>
          <p className="mt-6 text-xs uppercase tracking-[0.25em] text-amber-dim">
            original subscription run / 2026-09-25
          </p>
          <h1 className="mt-2 font-display text-4xl text-amber sm:text-5xl">
            GPT-5.6 Sol through Codex CLI
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-fg">
            One read-only headless Codex session per challenge and verdict, using a local
            ChatGPT sign-in. All 13 prompts finished. The same model judged its own answers.
          </p>
          <div className="mt-5 flex flex-wrap gap-x-6 gap-y-2 border-t border-amber-faint/60 pt-4 text-sm">
            <span><b className="text-amber-bright">{experimentData.average.toFixed(1)}/10</b> mean</span>
            <span><b className="text-amber-bright">{rows.length}/13</b> completed</span>
            <span className="text-fg-dim">judge: {experimentData.judge}</span>
          </div>
        </header>

        <section aria-labelledby="method-heading" className="border border-amber-faint bg-bg-raised/40 px-4 py-4">
          <h2 id="method-heading" className="text-xs uppercase tracking-[0.2em] text-amber-bright">
            How to read this run
          </h2>
          <p className="mt-2 max-w-3xl text-sm leading-relaxed text-fg">
            These scores now appear on the ChatGPT subscription board alongside GPT-6 Astra.
            Both runs use the same GPT-5.6 Sol judge, which graded its own answers here.
            Codex CLI follows an output-length instruction; it has no matching hard API token cap.
            The older Sonnet 5 scores remain in a separate archive.
          </p>
          <p className="mt-2 text-xs text-fg-dim">
            Doom and Slots were rescored after the judge was changed to read their full saved responses.
          </p>
        </section>

        <section aria-labelledby="breakdown-heading">
          <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
            <h2 id="breakdown-heading" className="text-xs uppercase tracking-[0.2em] text-fg-dim">
              Challenge breakdown
            </h2>
            <span className="text-xs text-fg-dim">open a row for the answer and verdict</span>
          </div>
          <div className="border-y border-amber-faint">
            {rows.map((row) => (
              <details key={row.challenge} className="group border-b border-amber-faint/60 last:border-0">
                <summary className="flex cursor-pointer list-none items-start justify-between gap-4 px-3 py-4 marker:hidden hover:bg-bg-raised/40 focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-amber">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                      <span className="font-mono text-sm font-semibold text-amber-bright">{row.challenge}</span>
                      <span className="text-xs text-fg-dim">{descriptions.get(row.challenge)}</span>
                    </div>
                    <div className="mt-2"><ScoreBreakdown row={row} /></div>
                  </div>
                  <span className={`shrink-0 font-display text-3xl ${scoreColor(row.total)}`}>
                    {row.total.toFixed(1)}
                  </span>
                </summary>
                <div className="px-3 pb-5">
                  <h3 className="text-xs uppercase tracking-wider text-fg-dim">Judge note</h3>
                  <p className="mt-1 max-w-3xl text-sm leading-relaxed text-fg">{row.notes}</p>
                  <h3 className="mt-5 text-xs uppercase tracking-wider text-fg-dim">Raw response</h3>
                  <pre className="mt-2 max-h-[36rem] overflow-auto border border-amber-faint bg-bg p-4 text-xs leading-relaxed text-fg"><code>{row.response}</code></pre>
                </div>
              </details>
            ))}
          </div>
        </section>

        <p className="text-xs text-fg-dim">
          <a className="text-amber hover:text-amber-bright" href="https://github.com/mager/mager-bench/blob/main/runs/2026-09-25-codex-cli-gpt-5.6-sol-rescored.json">
            Inspect the saved JSON run →
          </a>
          {" · "}
          <a className="text-amber hover:text-amber-bright" href="https://mager.co/notes/2026-09-25-codex-cli-bench">
            Read the note →
          </a>
        </p>
      </div>
    </main>
  );
}
