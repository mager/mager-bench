import Link from "next/link";
import resultsData from "@/data/results.json";
import fundingData from "@/data/funding.json";

type Challenge = {
  name: string;
  description: string;
  correctness: number;
  quality: number;
  documentation: number;
  total: number;
  speed_ms: number;
  notes: string;
  stddev?: number | null;
  runs?: number;
};

type ModelResult = {
  id: string;
  name: string;
  tier?: string;
  average: number;
  avg_speed_ms: number;
  avg_stddev?: number | null;
  runs?: number;
  challenges: Challenge[];
};

const data = resultsData as {
  generated_at: string;
  judge: string;
  judges?: string[];
  runs?: number;
  models: ModelResult[];
};

const funding = fundingData as {
  goal_cents: number;
  raised_cents: number;
  wishlist: { model_id: string; name: string; status: string; est_cost_cents: number }[];
};

function formatDate(iso: string) {
  return new Date(iso).toUTCString().replace("GMT", "UTC");
}

type Tier = "green" | "yellow" | "red";

function scoreTier(score: number): Tier {
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

const COST_TIER_STYLE: Record<string, string> = {
  free: "text-green",
  cheap: "text-cyan",
  paid: "text-magenta",
  unknown: "text-fg-dim",
};

function money(cents: number) {
  return `$${(cents / 100).toFixed(0)}`;
}

export default function Home() {
  const models = data.models;
  const top = models[0];
  const challengeCount = top?.challenges.length ?? 0;
  const fundPct = Math.min(
    100,
    Math.round((funding.raised_cents / Math.max(1, funding.goal_cents)) * 100)
  );
  const unfunded = funding.wishlist.filter((w) => w.status === "unfunded").length;
  const scoredIds = new Set(models.map((m) => m.id));

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
              v1.1 // {challengeCount}-challenge personal coding bench
            </span>
          </div>
          <p className="max-w-xl text-sm leading-relaxed text-fg">
            Opinionated coding tasks, scored by an LLM judge on{" "}
            <span className="font-semibold text-green">correctness</span>,{" "}
            <span className="font-semibold text-magenta">code quality</span>, and{" "}
            <span className="font-semibold text-cyan">documentation</span>. Free-tier models
            run free. Paid models get crowdfunded.
          </p>
        </header>

        {top && (
          <section
            className="rise flex flex-col items-start gap-8 sm:flex-row sm:items-center sm:justify-between"
            style={{ animationDelay: "80ms" }}
          >
            <div className="crt-flicker">
              <div className="text-xs uppercase tracking-[0.3em] text-fg-dim">
                #{String(1).padStart(2, "0")} {top.name}
              </div>
              <div
                className={`font-display text-[6.5rem] leading-none sm:text-[9rem] ${TIER_STYLE[scoreTier(top.average)].text} ${TIER_STYLE[scoreTier(top.average)].glow}`}
              >
                {top.average.toFixed(1)}
              </div>
              <div className="text-sm uppercase tracking-[0.3em] text-fg-dim">
                / 10 leader · {models.length} model{models.length === 1 ? "" : "s"} scored
              </div>
            </div>
            <dl className="grid grid-cols-2 gap-x-10 gap-y-4 text-sm sm:text-right">
              <div>
                <dt className="text-xs uppercase tracking-wider text-fg-dim">avg latency</dt>
                <dd className="mt-0.5 font-medium">{top.avg_speed_ms}ms</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wider text-fg-dim">challenges</dt>
                <dd className="mt-0.5 font-medium">{challengeCount}</dd>
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
        )}

        <section id="leaderboard" className="rise scroll-mt-6" style={{ animationDelay: "140ms" }}>
          <h2 className="mb-3 text-xs uppercase tracking-[0.3em] text-fg-dim">leaderboard</h2>
          <div className="overflow-x-auto border border-amber-faint">
            <table className="w-full min-w-[560px] border-collapse text-sm">
              <thead>
                <tr className="border-b border-amber-faint text-left text-xs uppercase tracking-wider text-fg-dim">
                  <th className="px-4 py-3 font-normal">#</th>
                  <th className="px-4 py-3 font-normal">model</th>
                  <th className="px-4 py-3 font-normal">cost</th>
                  <th className="px-4 py-3 text-right font-normal">avg score</th>
                  <th className="px-4 py-3 text-right font-normal">avg latency</th>
                  <th className="px-4 py-3 text-right font-normal">n</th>
                </tr>
              </thead>
              <tbody>
                {models.map((m, i) => {
                  const style = TIER_STYLE[scoreTier(m.average)];
                  const cost = m.tier ?? "unknown";
                  return (
                    <tr
                      key={m.id}
                      className="lift border-b border-amber-faint/60 last:border-0"
                    >
                      <td className="px-4 py-3 text-fg-dim">{String(i + 1).padStart(2, "0")}</td>
                      <td className="px-4 py-3 font-medium">
                        <a href={`#model-${m.id}`} className="inline-flex items-center gap-2 hover:text-amber-bright">
                          <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
                          {m.name}
                        </a>
                      </td>
                      <td className={`px-4 py-3 text-xs uppercase tracking-wider ${COST_TIER_STYLE[cost] ?? COST_TIER_STYLE.unknown}`}>
                        {cost}
                      </td>
                      <td className={`px-4 py-3 text-right ${style.text} ${style.glow}`}>
                        {m.average.toFixed(1)}
                        {m.avg_stddev != null && m.avg_stddev > 0 && (
                          <span className="ml-1 text-xs text-fg-dim">±{m.avg_stddev}</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right text-fg-dim">{m.avg_speed_ms}ms</td>
                      <td className="px-4 py-3 text-right text-fg-dim">{m.challenges.length}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-fg-dim">
            free + cheap run by default. paid models land when{" "}
            <Link href="/fund" className="text-amber hover:text-amber-bright">
              crowdfunded
            </Link>{" "}
            or when you run them yourself.
          </p>
        </section>

        <section
          className="rise border border-amber-faint bg-bg-raised/40 px-4 py-4"
          style={{ animationDelay: "180ms" }}
        >
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-xs uppercase tracking-[0.3em] text-fg-dim">fund the bench</h2>
              <p className="mt-1 max-w-lg text-sm text-fg">
                {unfunded} paid model{unfunded === 1 ? "" : "s"} still waiting. Free tiers
                (Groq / Gemini) never need a card — crowdfunding buys the expensive head-to-heads.
              </p>
            </div>
            <Link
              href="/fund"
              className="border border-amber bg-amber/15 px-4 py-2 text-sm font-medium text-amber-bright hover:bg-amber/25"
            >
              open fund drive →
            </Link>
          </div>
          <div className="mt-4 h-2 w-full border border-amber-faint bg-bg">
            <div className="h-full bg-amber" style={{ width: `${fundPct}%` }} />
          </div>
          <p className="mt-2 text-xs text-fg-dim">
            {money(funding.raised_cents)} / {money(funding.goal_cents)} season goal · {fundPct}%
          </p>
        </section>

        {models.map((model, mi) => (
          <section
            key={model.id}
            id={`model-${model.id}`}
            className="rise flex scroll-mt-6 flex-col gap-4"
            style={{ animationDelay: `${200 + mi * 40}ms` }}
          >
            <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-amber-faint pb-2">
              <h2 className="text-xs uppercase tracking-[0.3em] text-fg-dim">
                <span className="text-amber-bright">{model.name}</span>
                {" — "}challenge breakdown
                {" · "}
                <Link
                  href={`/models/${model.id}`}
                  className="normal-case tracking-normal text-amber hover:text-amber-bright"
                >
                  inspect traces →
                </Link>
              </h2>
              <div className="flex items-center gap-3 text-xs text-fg-dim">
                <span className={`uppercase tracking-wider ${COST_TIER_STYLE[model.tier ?? "unknown"]}`}>
                  {model.tier ?? "unknown"}
                </span>
                <span className={`font-display text-2xl ${TIER_STYLE[scoreTier(model.average)].text}`}>
                  {model.average.toFixed(1)}
                </span>
              </div>
            </div>
            {model.challenges.map((c) => {
              const t = scoreTier(c.total);
              const style = TIER_STYLE[t];
              return (
                <article
                  key={`${model.id}-${c.name}`}
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
        ))}

        <section
          className="rise border border-amber-faint px-4 py-4"
          style={{ animationDelay: "300ms" }}
        >
          <h2 className="mb-2 text-xs uppercase tracking-[0.3em] text-fg-dim">not scored yet</h2>
          <ul className="flex flex-col gap-1 text-sm text-fg-dim">
            {funding.wishlist
              .filter((w) => !scoredIds.has(w.model_id))
              .map((w) => (
                <li key={w.model_id} className="flex flex-wrap items-baseline gap-x-3">
                  <span className="text-amber-bright">{w.name}</span>
                  <span className="text-xs uppercase tracking-wider">{w.status}</span>
                  <span>
                    {w.est_cost_cents === 0 ? "free to run" : `~${money(w.est_cost_cents)} / full suite`}
                  </span>
                </li>
              ))}
          </ul>
          <Link href="/fund" className="mt-3 inline-block text-xs text-amber hover:text-amber-bright">
            put them on the board →
          </Link>
        </section>

        <section
          id="api"
          className="rise scroll-mt-6 border border-amber-faint bg-bg-raised/40 px-4 py-4 text-xs"
          style={{ animationDelay: "320ms" }}
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
