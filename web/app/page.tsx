import resultsData from "@/data/results.json";

type Challenge = {
  name: string;
  description: string;
  correctness: number;
  quality: number;
  documentation: number;
  total: number;
  speed_ms: number;
  notes: string;
};

type ModelResult = {
  id: string;
  name: string;
  average: number;
  avg_speed_ms: number;
  challenges: Challenge[];
};

const data = resultsData as {
  generated_at: string;
  judge: string;
  models: ModelResult[];
};

function formatDate(iso: string) {
  return new Date(iso).toUTCString().replace("GMT", "UTC");
}

function scoreLabel(score: number) {
  if (score >= 8.5) return "EXCELLENT";
  if (score >= 7) return "SOLID";
  if (score >= 5) return "MIXED";
  return "REGRESSION";
}

export default function Home() {
  const top = data.models[0];

  return (
    <div className="min-h-screen px-4 py-10 sm:px-8 md:py-16">
      <div className="mx-auto flex max-w-4xl flex-col gap-10">
        <header
          className="rise flex flex-col gap-2 border-b border-amber-faint pb-5"
          style={{ animationDelay: "0ms" }}
        >
          <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
            <h1 className="glow font-display text-4xl tracking-wide sm:text-5xl">
              mager-bench
            </h1>
            <span className="text-xs text-amber-dim">
              v1.0 // personal coding-model benchmark
            </span>
          </div>
          <p className="max-w-xl text-sm leading-relaxed text-amber-dim">
            Five tasks I actually care about, scored by an LLM judge on correctness, code
            quality, and documentation.{" "}
            <a
              className="text-amber underline decoration-dotted underline-offset-4 hover:text-amber-bright"
              href="https://github.com/mager/mager-bench"
              target="_blank"
              rel="noreferrer"
            >
              source →
            </a>
          </p>
        </header>

        <section
          className="rise flex flex-col items-start gap-8 sm:flex-row sm:items-center sm:justify-between"
          style={{ animationDelay: "80ms" }}
        >
          <div className="crt-flicker">
            <div className="text-xs uppercase tracking-[0.3em] text-amber-dim">{top.name}</div>
            <div className="glow-strong font-display text-[6.5rem] leading-none sm:text-[9rem]">
              {top.average.toFixed(1)}
            </div>
            <div className="text-sm uppercase tracking-[0.3em] text-amber-dim">
              / 10 average score
            </div>
          </div>
          <dl className="grid grid-cols-2 gap-x-10 gap-y-4 text-sm sm:text-right">
            <div>
              <dt className="text-xs uppercase tracking-wider text-amber-dim">avg latency</dt>
              <dd className="mt-0.5 font-medium">{top.avg_speed_ms}ms</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-amber-dim">challenges</dt>
              <dd className="mt-0.5 font-medium">{top.challenges.length}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-amber-dim">judge</dt>
              <dd className="mt-0.5 font-medium">{data.judge}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-amber-dim">last run</dt>
              <dd className="mt-0.5 font-medium">{formatDate(data.generated_at)}</dd>
            </div>
          </dl>
        </section>

        <section className="rise" style={{ animationDelay: "140ms" }}>
          <h2 className="mb-3 text-xs uppercase tracking-[0.3em] text-amber-dim">leaderboard</h2>
          <div className="overflow-x-auto border border-amber-faint">
            <table className="w-full min-w-[480px] border-collapse text-sm">
              <thead>
                <tr className="border-b border-amber-faint text-left text-xs uppercase tracking-wider text-amber-dim">
                  <th className="px-4 py-3 font-normal">#</th>
                  <th className="px-4 py-3 font-normal">model</th>
                  <th className="px-4 py-3 text-right font-normal">avg score</th>
                  <th className="px-4 py-3 text-right font-normal">avg latency</th>
                </tr>
              </thead>
              <tbody>
                {data.models.map((m, i) => (
                  <tr key={m.id} className="border-b border-amber-faint/60 last:border-0">
                    <td className="px-4 py-3 text-amber-dim">{String(i + 1).padStart(2, "0")}</td>
                    <td className="px-4 py-3 font-medium">{m.name}</td>
                    <td className="glow px-4 py-3 text-right">{m.average.toFixed(1)}</td>
                    <td className="px-4 py-3 text-right text-amber-dim">{m.avg_speed_ms}ms</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-amber-dim">
            more models land here as they get run — see the CLI.
          </p>
        </section>

        <section className="rise flex flex-col gap-4" style={{ animationDelay: "200ms" }}>
          <h2 className="text-xs uppercase tracking-[0.3em] text-amber-dim">
            {top.name} — challenge breakdown
          </h2>
          {top.challenges.map((c) => {
            const isAlert = c.total < 5;
            return (
              <article key={c.name} className="border border-amber-faint bg-bg-raised/40 px-4 py-3">
                <div className="flex items-center gap-3">
                  <h3 className="whitespace-nowrap font-display text-lg tracking-wide">
                    {c.name}
                  </h3>
                  <div
                    className="h-px flex-1"
                    style={{
                      backgroundImage:
                        "repeating-linear-gradient(to right, var(--amber-dim) 0, var(--amber-dim) 4px, transparent 4px, transparent 8px)",
                    }}
                  />
                  <span
                    className={`font-display text-2xl ${isAlert ? "glow-alert text-alert" : "glow"}`}
                  >
                    {c.total.toFixed(1)}
                  </span>
                </div>
                <p className="mt-1 text-xs text-amber-dim">{c.description}</p>

                <div className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-xs text-amber-dim">
                  <span>
                    correctness <b className="text-amber">{c.correctness.toFixed(1)}</b>
                  </span>
                  <span>
                    quality <b className="text-amber">{c.quality.toFixed(1)}</b>
                  </span>
                  <span>
                    documentation <b className="text-amber">{c.documentation.toFixed(1)}</b>
                  </span>
                  <span>{c.speed_ms}ms</span>
                  {isAlert && (
                    <span className="glow-alert text-alert">⚠ {scoreLabel(c.total)}</span>
                  )}
                </div>

                <p className="mt-3 border-l-2 border-amber-faint pl-3 text-xs italic text-amber-dim">
                  # {c.notes}
                </p>
              </article>
            );
          })}
        </section>

        <section
          className="rise border border-amber-faint bg-bg-raised/40 px-4 py-4 text-xs"
          style={{ animationDelay: "260ms" }}
        >
          <h2 className="mb-2 text-xs uppercase tracking-[0.3em] text-amber-dim">api</h2>
          <p className="text-amber-dim">
            $ curl{" "}
            <a
              className="text-amber underline decoration-dotted underline-offset-4 hover:text-amber-bright"
              href="/api/results"
            >
              /api/results
            </a>{" "}
            → 200 OK
          </p>
          <p className="mt-1 text-amber-dim">
            Same data behind this page, as JSON. Cached 1h at the edge.
          </p>
        </section>

        <footer
          className="rise flex flex-wrap items-center justify-between gap-2 border-t border-amber-faint pt-4 text-xs text-amber-dim"
          style={{ animationDelay: "320ms" }}
        >
          <span>mager-bench</span>
          <span className="cursor">READY</span>
        </footer>
      </div>
    </div>
  );
}
