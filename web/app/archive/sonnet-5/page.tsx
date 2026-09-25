import type { Metadata } from "next";
import Link from "next/link";
import archiveData from "@/data/sonnet-5-board.json";

export const metadata: Metadata = {
  title: "Sonnet 5 board archive — mager-bench",
  description: "The original API-model leaderboard, preserved with its Sonnet 5 judge and raw responses.",
};

type ArchivedChallenge = {
  name: string;
  total: number;
  notes: string;
  run_details?: { response: string }[];
};
type ArchivedModel = {
  id: string;
  name: string;
  average: number;
  avg_stddev?: number | null;
  challenges: ArchivedChallenge[];
};
const archive = archiveData as {
  generated_at: string;
  judge: string;
  models: ArchivedModel[];
};

export default function SonnetArchive() {
  return (
    <main className="px-4 py-10 sm:px-8 md:py-16">
      <div className="mx-auto flex max-w-4xl flex-col gap-9">
        <header className="border-b border-amber-faint pb-6">
          <Link href="/" className="text-xs text-fg-dim hover:text-amber-bright">← current leaderboard</Link>
          <p className="mt-6 text-xs uppercase tracking-[0.25em] text-amber-dim">historical board / API era</p>
          <h1 className="mt-2 font-display text-4xl text-amber sm:text-5xl">Sonnet 5 board archive</h1>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-fg">
            These {archive.models.length} models were scored by {archive.judge}. Their numbers
            belong to this earlier judge and should not be ranked against the current
            ChatGPT-subscription runs.
          </p>
          <p className="mt-3 text-xs text-fg-dim">Last updated {new Date(archive.generated_at).toUTCString()}</p>
        </header>

        <section>
          <h2 className="mb-3 text-xs uppercase tracking-[0.3em] text-fg-dim">Archived ranking</h2>
          <div className="border-y border-amber-faint">
            {archive.models.map((model, index) => (
              <details key={model.id} className="border-b border-amber-faint/60 last:border-0">
                <summary className="flex cursor-pointer items-baseline justify-between gap-4 px-3 py-4 hover:bg-bg-raised/40">
                  <span className="font-mono text-sm text-fg">
                    <span className="mr-5 text-fg-dim">{String(index + 1).padStart(2, "0")}</span>
                    {model.name}
                  </span>
                  <span className="font-display text-3xl text-amber">
                    {model.average.toFixed(1)}
                    {model.avg_stddev != null && model.avg_stddev > 0 && (
                      <small className="ml-1 font-mono text-xs text-fg-dim">±{model.avg_stddev}</small>
                    )}
                  </span>
                </summary>
                <div className="space-y-2 px-3 pb-5">
                  {model.challenges.map((challenge) => (
                    <details key={challenge.name} className="border border-amber-faint/60 px-3 py-2">
                      <summary className="flex cursor-pointer justify-between gap-3 text-sm text-fg">
                        <span>{challenge.name}</span>
                        <span className="text-amber-bright">{challenge.total.toFixed(1)}</span>
                      </summary>
                      <p className="mt-2 text-xs leading-relaxed text-fg-dim">{challenge.notes}</p>
                      {challenge.run_details?.[0]?.response && (
                        <pre className="mt-3 max-h-96 overflow-auto bg-bg p-3 text-xs leading-relaxed text-fg"><code>{challenge.run_details[0].response}</code></pre>
                      )}
                    </details>
                  ))}
                </div>
              </details>
            ))}
          </div>
        </section>

        <a className="text-xs text-amber hover:text-amber-bright" href="https://github.com/mager/mager-bench/blob/main/runs/2026-09-25-sonnet-5-board-archive.json">
          Inspect the original merged JSON →
        </a>
      </div>
    </main>
  );
}
