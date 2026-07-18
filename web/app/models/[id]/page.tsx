import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import resultsData from "@/data/results.json";

type ChallengeResult = {
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
  challenges: ChallengeResult[];
};

const data = resultsData as {
  generated_at: string;
  judge: string;
  models: ModelResult[];
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

function tier(score: number) {
  if (score > 9.5) return { text: "text-green", glow: "glow-green" };
  if (score >= 7) return { text: "text-amber", glow: "glow" };
  return { text: "text-alert", glow: "glow-alert" };
}

export function generateStaticParams() {
  return data.models.map((m) => ({ id: m.id }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const m = data.models.find((x) => x.id === id);
  return {
    title: m ? `${m.name} runs — mager-bench` : "model runs — mager-bench",
    description: m
      ? `Every ${m.name} run on mager-bench: per-challenge scores and full response traces.`
      : undefined,
  };
}

export default async function ModelPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const model = data.models.find((m) => m.id === id);
  if (!model) return notFound();

  const t = tier(model.average);
  const runCount = model.runs ?? 1;

  return (
    <div className="px-4 py-10 sm:px-8 md:py-16">
      <div className="mx-auto flex max-w-4xl flex-col gap-10">
        <header className="rise flex flex-col gap-2 border-b border-amber-faint pb-5">
          <Link href="/" className="text-xs text-fg-dim hover:text-amber-bright">
            ← leaderboard
          </Link>
          <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
            <h1 className="glow font-display text-4xl tracking-wide text-amber sm:text-5xl">
              {model.name}
            </h1>
            <span className={`font-display text-5xl ${t.text} ${t.glow}`}>
              {model.average.toFixed(1)}
            </span>
          </div>
          <div className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-fg-dim">
            <span className={`uppercase tracking-wider ${COST_TIER_STYLE[model.tier ?? "unknown"]}`}>
              {model.tier ?? "unknown"} tier
            </span>
            <span>
              {runCount} run{runCount === 1 ? "" : "s"} per challenge
            </span>
            <span>avg {model.avg_speed_ms}ms</span>
            <span>judged by {data.judge}</span>
          </div>
          <p className="max-w-xl text-sm leading-relaxed text-fg">
            Every challenge this model has run, with the full paper trail — click into any
            row to read the raw response the judge scored.
          </p>
        </header>

        <section className="rise flex flex-col gap-3" style={{ animationDelay: "80ms" }}>
          <h2 className="text-xs uppercase tracking-[0.3em] text-fg-dim">
            {model.challenges.length} challenges · best to worst
          </h2>
          {model.challenges.map((c) => {
            const ct = tier(c.total);
            return (
              <Link
                key={c.name}
                href={`/models/${model.id}/${c.name}`}
                className="lift group border border-amber-faint bg-bg-raised/40 px-4 py-4"
              >
                <div className="flex items-center gap-3">
                  <h3 className="whitespace-nowrap font-mono text-base font-semibold tracking-wide text-amber-bright group-hover:text-amber">
                    {c.name}
                  </h3>
                  <div
                    className="h-px flex-1"
                    style={{
                      backgroundImage:
                        "repeating-linear-gradient(to right, var(--amber-dim) 0, var(--amber-dim) 4px, transparent 4px, transparent 8px)",
                    }}
                  />
                  <span className={`font-display text-2xl ${ct.text} ${ct.glow}`}>
                    {c.total.toFixed(1)}
                    {c.stddev != null && c.stddev > 0 && (
                      <span className="ml-1 font-mono text-xs text-fg-dim">±{c.stddev}</span>
                    )}
                  </span>
                </div>
                <div className="mt-2 flex flex-wrap gap-x-6 gap-y-1.5 text-sm text-fg-dim">
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
                    <span className={`h-1.5 w-1.5 rounded-full ${DIMENSION_STYLE.documentation.dot}`} />
                    documentation{" "}
                    <b className={`font-semibold ${DIMENSION_STYLE.documentation.text}`}>
                      {c.documentation.toFixed(1)}
                    </b>
                  </span>
                  <span>{c.speed_ms}ms</span>
                  <span className="ml-auto text-amber-dim transition-transform group-hover:translate-x-0.5">
                    inspect trace →
                  </span>
                </div>
              </Link>
            );
          })}
        </section>
      </div>
    </div>
  );
}
