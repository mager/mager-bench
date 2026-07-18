import Link from "next/link";
import type { Metadata } from "next";
import fundingData from "@/data/funding.json";
import resultsData from "@/data/results.json";

export const metadata: Metadata = {
  title: "fund the bench — mager-bench",
  description:
    "Crowdfund paid-model evals for mager-bench. Free tiers run free; pitch in for Opus, GPT-4o, and friends.",
};

type Funding = {
  headline: string;
  tagline: string;
  goal_cents: number;
  raised_cents: number;
  currency: string;
  links: { label: string; href: string | null; primary?: boolean }[];
  tiers: {
    id: string;
    name: string;
    amount_cents: number;
    perks: string[];
  }[];
  wishlist: {
    model_id: string;
    name: string;
    tier: string;
    why: string;
    est_cost_cents: number;
    status: string;
  }[];
  principles: string[];
};

type Results = {
  models: { id: string; name: string; average: number; tier?: string }[];
};

const funding = fundingData as Funding;
const results = resultsData as Results;

function money(cents: number) {
  return `$${(cents / 100).toFixed(cents % 100 === 0 ? 0 : 2)}`;
}

function statusStyle(status: string) {
  if (status === "scored") return "text-green";
  if (status === "ready") return "text-cyan";
  if (status === "funded") return "text-amber-bright";
  return "text-fg-dim";
}

export default function FundPage() {
  const pct = Math.min(
    100,
    Math.round((funding.raised_cents / Math.max(1, funding.goal_cents)) * 100)
  );
  const scoredIds = new Set(results.models.map((m) => m.id));

  return (
    <div className="min-h-screen px-4 py-10 sm:px-8 md:py-16">
      <div className="mx-auto flex max-w-4xl flex-col gap-10">
        <header className="rise flex flex-col gap-2 border-b border-amber-faint pb-5">
          <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
            <h1 className="glow font-display text-4xl tracking-wide text-amber sm:text-5xl">
              {funding.headline}
            </h1>
            <Link href="/" className="text-xs text-fg-dim hover:text-amber-bright">
              ← leaderboard
            </Link>
          </div>
          <p className="max-w-2xl text-sm leading-relaxed text-fg">{funding.tagline}</p>
        </header>

        <section className="rise border border-amber-faint bg-bg-raised/40 px-4 py-5" style={{ animationDelay: "60ms" }}>
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <div className="text-xs uppercase tracking-[0.3em] text-fg-dim">season goal</div>
              <div className="font-display text-5xl text-amber glow">
                {money(funding.raised_cents)}
                <span className="text-2xl text-fg-dim"> / {money(funding.goal_cents)}</span>
              </div>
            </div>
            <div className="text-sm text-fg-dim">{pct}% funded</div>
          </div>
          <div className="mt-4 h-3 w-full border border-amber-faint bg-bg">
            <div
              className="h-full bg-amber transition-all"
              style={{ width: `${pct}%`, boxShadow: "0 0 12px rgba(255,176,0,0.45)" }}
            />
          </div>
          <div className="mt-5 flex flex-wrap gap-3">
            {funding.links.map((l) =>
              l.href ? (
                <a
                  key={l.label}
                  href={l.href}
                  target="_blank"
                  rel="noreferrer"
                  className={
                    l.primary
                      ? "border border-amber bg-amber/15 px-4 py-2 text-sm font-medium text-amber-bright hover:bg-amber/25"
                      : "border border-amber-faint px-4 py-2 text-sm text-fg hover:border-amber-dim hover:text-amber-bright"
                  }
                >
                  {l.label} →
                </a>
              ) : (
                <span
                  key={l.label}
                  className="border border-amber-faint/60 px-4 py-2 text-sm text-fg-dim"
                >
                  {l.label}
                </span>
              )
            )}
          </div>
        </section>

        <section className="rise" style={{ animationDelay: "120ms" }}>
          <h2 className="mb-3 text-xs uppercase tracking-[0.3em] text-fg-dim">support tiers</h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {funding.tiers.map((t) => (
              <article
                key={t.id}
                className="lift flex flex-col gap-2 border border-amber-faint bg-bg-raised/40 px-4 py-4"
              >
                <div className="text-xs uppercase tracking-wider text-fg-dim">{t.id}</div>
                <h3 className="font-mono text-base font-semibold text-amber-bright">{t.name}</h3>
                <div className="font-display text-3xl text-amber">{money(t.amount_cents)}</div>
                <ul className="mt-2 flex flex-col gap-1.5 text-sm text-fg">
                  {t.perks.map((p) => (
                    <li key={p} className="flex gap-2">
                      <span className="text-amber-dim">›</span>
                      <span>{p}</span>
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </section>

        <section className="rise" style={{ animationDelay: "180ms" }}>
          <h2 className="mb-3 text-xs uppercase tracking-[0.3em] text-fg-dim">
            model wishlist — what your $ buys
          </h2>
          <div className="overflow-x-auto border border-amber-faint">
            <table className="w-full min-w-[560px] border-collapse text-sm">
              <thead>
                <tr className="border-b border-amber-faint text-left text-xs uppercase tracking-wider text-fg-dim">
                  <th className="px-4 py-3 font-normal">model</th>
                  <th className="px-4 py-3 font-normal">tier</th>
                  <th className="px-4 py-3 font-normal">why</th>
                  <th className="px-4 py-3 text-right font-normal">est.</th>
                  <th className="px-4 py-3 text-right font-normal">status</th>
                </tr>
              </thead>
              <tbody>
                {funding.wishlist.map((w) => {
                  const status = scoredIds.has(w.model_id) ? "scored" : w.status;
                  return (
                    <tr key={w.model_id} className="border-b border-amber-faint/60 last:border-0">
                      <td className="px-4 py-3 font-medium text-amber-bright">{w.name}</td>
                      <td className="px-4 py-3 text-fg-dim">{w.tier}</td>
                      <td className="px-4 py-3 text-fg">{w.why}</td>
                      <td className="px-4 py-3 text-right text-fg-dim">
                        {w.est_cost_cents === 0 ? "free" : money(w.est_cost_cents)}
                      </td>
                      <td className={`px-4 py-3 text-right uppercase tracking-wider text-xs ${statusStyle(status)}`}>
                        {status}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-fg-dim">
            already on the board:{" "}
            {results.models.map((m) => m.name).join(" · ") || "nobody yet — be the first funder"}
          </p>
        </section>

        <section className="rise border border-amber-faint bg-bg-raised/40 px-4 py-4" style={{ animationDelay: "240ms" }}>
          <h2 className="mb-3 text-xs uppercase tracking-[0.3em] text-fg-dim">how the money works</h2>
          <ul className="flex flex-col gap-2 text-sm text-fg">
            {funding.principles.map((p) => (
              <li key={p} className="flex gap-2">
                <span className="text-green">✓</span>
                <span>{p}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="rise border border-amber-faint px-4 py-4 text-sm text-fg" style={{ animationDelay: "280ms" }}>
          <h2 className="mb-2 text-xs uppercase tracking-[0.3em] text-fg-dim">run it yourself for $0</h2>
          <pre className="overflow-x-auto bg-bg/60 px-3 py-3 text-xs text-fg-dim">
{`# free subjects + free judge — no paid APIs required
export GROQ_API_KEY=...
export GEMINI_API_KEY=...
python bench.py --tier free --judge gemini-2.0-flash --runs 3 --output results.json
cd web && node scripts/sync-results.mjs && npm run dev`}
          </pre>
        </section>

        <footer className="rise border-t border-amber-faint pt-4 text-xs text-fg-dim" style={{ animationDelay: "320ms" }}>
          <Link href="/" className="hover:text-amber-bright">
            ← back to scores
          </Link>
        </footer>
      </div>
    </div>
  );
}
