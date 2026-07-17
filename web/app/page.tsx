import Link from "next/link";
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

type Tier = "green" | "yellow" | "red";

function tier(score: number): Tier {
  if (score > 9.5) return "green";
  if (score >= 7) return "yellow";
  return "red";
}

const TIER_LABEL: Record<Tier, string> = {
  green: "TOP SCORE",
  yellow: "SOLID",
  red: "LOW SCORE",
};

const TIER_STYLE: Record<Tier, { dot: string; text: string; glow: string }> = {
  green: { dot: "bg-green", text: "text-green", glow: "glow-green" },
  yellow: { dot: "bg-amber", text: "text-amber", glow: "glow" },
  red: { dot: "bg-alert", text: "text-alert", glow: "glow-alert" },
};

const DIMENSION_STYLE = {
  correctness: { dot: "bg-green", text: "text-green" },
  quality: { dot: "bg-magenta", text: "text-magenta" },
  documentation: { dot: "bg-cyan", text: "text-cyan" },
} as const;

export default function Home() {
  const top = data.models[0];

  return (
    <div className="px-4 py-10 sm:px-8 md:py-16">
      <div className="mx-auto flex max-w-4xl flex-col gap-10">
        <header
          className="rise flex flex-col gap-2 border-b border-amber-faint pb-5"
          style={{ animationDelay: "0ms" }}
        >
          <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
            <h1 className="glow font-display text-4xl tracking-wide text-amber sm:text-5xl">
              mager-bench
            </h1>
            <span className="text-xs text-fg-dim">
              v1.0 // personal coding-model benchmark
            </span>
          </div>
          <p className="max-w-xl text-sm leading-relaxed text-fg">
            {top.challenges.length} tasks I actually care about, scored by an LLM judge on{" "}
            <span className="font-semibold text-green">correctness</span>,{" "}
            <span className="font-semibold text-magenta">code quality</span>, and{" "}
            <span className="font-semibold text-cyan">documentation</span>. A benchmark
            models have to earn.
          </p>
        </header>

        <section
          className="rise flex flex-col items-start gap-8 sm:flex-row sm:items-center sm:justify-between"
          style={{ animationDelay: "80ms" }}
        >
          <div className="crt-flicker">
            <div className="text-xs uppercase tracking-[0.3em] text-fg-dim">{top.name}</div>
            <div
              className={`font-display text-[6.5rem] leading-none sm:text-[9rem] ${TIER_STYLE[tier(top.average)].text} ${TIER_STYLE[tier(top.average)].glow}`}
            >
              {top.average.toFixed(1)}
            </div>
            <div className="text-sm uppercase tracking-[0.3em] text-fg-dim">
              / 10 average score
            </div>
          </div>
          <dl className="grid grid-cols-2 gap-x-10 gap-y-4 text-sm sm:text-right">
            <div>
              <dt className="text-xs uppercase tracking-wider text-fg-dim">avg latency</dt>
              <dd className="mt-0.5 font-medium">{top.avg_speed_ms}ms</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-fg-dim">challenges</dt>
              <dd className="mt-0.5 font-medium">{top.challenges.length}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-fg-dim">judge</dt>
              <dd className="mt-0.5 font-medium">{data.judge}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-fg-dim">last run</dt>
              <dd className="mt-0.5 font-medium">{formatDate(data.generated_at)}</dd>
            </div>
          </dl>
        </section>

        <section id="leaderboard" className="rise scroll-mt-6" style={{ animationDelay: "140ms" }}>
          <h2 className="mb-3 text-xs uppercase tracking-[0.3em] text-fg-dim">leaderboard</h2>
          <div className="overflow-x-auto border border-amber-faint">
            <table className="w-full min-w-[480px] border-collapse text-sm">
              <thead>
                <tr className="border-b border-amber-faint text-left text-xs uppercase tracking-wider text-fg-dim">
                  <th className="px-4 py-3 font-normal">#</th>
                  <th className="px-4 py-3 font-normal">model</th>
                  <th className="px-4 py-3 text-right font-normal">avg score</th>
                  <th className="px-4 py-3 text-right font-normal">avg latency</th>
                </tr>
              </thead>
              <tbody>
                {data.models.map((m, i) => {
                  const style = TIER_STYLE[tier(m.average)];
                  return (
                    <tr
                      key={m.id}
                      className="lift border-b border-amber-faint/60 last:border-0"
                    >
                      <td className="px-4 py-3 text-fg-dim">{String(i + 1).padStart(2, "0")}</td>
                      <td className="px-4 py-3 font-medium">
                        <span className="inline-flex items-center gap-2">
                          <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
                          {m.name}
                        </span>
                      </td>
                      <td className={`px-4 py-3 text-right ${style.text} ${style.glow}`}>
                        {m.average.toFixed(1)}
                      </td>
                      <td className="px-4 py-3 text-right text-fg-dim">{m.avg_speed_ms}ms</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-fg-dim">
            more models land here as they get run — see the CLI.
          </p>
        </section>

        <section className="rise flex flex-col gap-4" style={{ animationDelay: "200ms" }}>
          <h2 className="text-xs uppercase tracking-[0.3em] text-fg-dim">
            {top.name} — challenge breakdown
          </h2>
          {top.challenges.map((c) => {
            const t = tier(c.total);
            const style = TIER_STYLE[t];
            return (
              <article
                key={c.name}
                className="lift border border-amber-faint bg-bg-raised/40 px-4 py-4"
              >
                <div className="flex items-center gap-3">
                  <Link
                    href={`/challenges/${c.name}`}
                    className="group whitespace-nowrap font-mono text-base font-semibold tracking-wide text-amber-bright hover:text-amber"
                  >
                    {c.name}
                    <span className="ml-1.5 inline-block text-amber-dim transition-transform group-hover:translate-x-0.5">
                      →
                    </span>
                  </Link>
                  <div
                    className="h-px flex-1"
                    style={{
                      backgroundImage:
                        "repeating-linear-gradient(to right, var(--amber-dim) 0, var(--amber-dim) 4px, transparent 4px, transparent 8px)",
                    }}
                  />
                  <span className={`font-display text-2xl ${style.text} ${style.glow}`}>
                    {c.total.toFixed(1)}
                  </span>
                </div>
                <p className="mt-1.5 text-sm leading-relaxed text-fg">{c.description}</p>

                <div className="mt-3 flex flex-wrap gap-x-6 gap-y-1.5 text-sm text-fg-dim">
                  <span className="inline-flex items-center gap-1.5">
                    <span className={`h-1.5 w-1.5 rounded-full ${DIMENSION_STYLE.correctness.dot}`} />
                    correctness{" "}
                    <b className={`font-semibold ${DIMENSION_STYLE.correctness.text}`}>
                      {c.correctness.toFixed(1)}
                    </b>
                  </span>
                  <span className="inline-flex items-center gap-1.5">
                    <span className={`h-1.5 w-1.5 rounded-full ${DIMENSION_STYLE.quality.dot}`} />
                    quality{" "}
                    <b className={`font-semibold ${DIMENSION_STYLE.quality.text}`}>
                      {c.quality.toFixed(1)}
                    </b>
                  </span>
                  <span className="inline-flex items-center gap-1.5">
                    <span
                      className={`h-1.5 w-1.5 rounded-full ${DIMENSION_STYLE.documentation.dot}`}
                    />
                    documentation{" "}
                    <b className={`font-semibold ${DIMENSION_STYLE.documentation.text}`}>
                      {c.documentation.toFixed(1)}
                    </b>
                  </span>
                  <span>{c.speed_ms}ms</span>
                  {t !== "yellow" && (
                    <span className={`${style.text} ${style.glow}`}>
                      {t === "green" ? "▲" : "⚠"} {TIER_LABEL[t]}
                    </span>
                  )}
                </div>

                <p className="mt-3 bg-bg/50 px-3 py-2 text-sm leading-relaxed text-fg">
                  <span className="text-amber-dim"># </span>
                  {c.notes}
                </p>
              </article>
            );
          })}
        </section>

        <section
          id="api"
          className="rise scroll-mt-6 border border-amber-faint bg-bg-raised/40 px-4 py-4 text-xs"
          style={{ animationDelay: "260ms" }}
        >
          <h2 className="mb-2 text-xs uppercase tracking-[0.3em] text-fg-dim">api</h2>
          <p className="text-fg-dim">
            $ curl{" "}
            <a
              className="text-amber underline decoration-dotted underline-offset-4 hover:text-amber-bright"
              href="/api/results"
            >
              /api/results
            </a>{" "}
            → 200 OK
          </p>
          <p className="mt-1 text-fg-dim">
            Same data behind this page, as JSON. Cached 1h at the edge.
          </p>
        </section>

      </div>
    </div>
  );
}
