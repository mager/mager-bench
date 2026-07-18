import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import challengesData from "@/data/challenges.json";
import resultsData from "@/data/results.json";

type ChallengeDef = {
  name: string;
  description: string;
  prompt: string;
};

type RunDetail = {
  run: number;
  correctness: number;
  quality: number;
  documentation: number;
  total: number;
  speed_ms: number;
  notes: string;
  response: string;
};

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
  run_details?: RunDetail[];
};

type ModelResult = {
  id: string;
  name: string;
  tier?: string;
  challenges: ChallengeResult[];
};

const challenges = challengesData as ChallengeDef[];
const data = resultsData as { judge: string; models: ModelResult[] };

const DIMENSION_STYLE = {
  correctness: { dot: "bg-green", text: "text-green" },
  quality: { dot: "bg-magenta", text: "text-magenta" },
  documentation: { dot: "bg-cyan", text: "text-cyan" },
} as const;

function tier(score: number) {
  if (score > 9.5) return { text: "text-green", glow: "glow-green" };
  if (score >= 7) return { text: "text-amber", glow: "glow" };
  return { text: "text-alert", glow: "glow-alert" };
}

export function generateStaticParams() {
  return data.models.flatMap((m) =>
    m.challenges.map((c) => ({ id: m.id, challenge: c.name }))
  );
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string; challenge: string }>;
}): Promise<Metadata> {
  const { id, challenge } = await params;
  const m = data.models.find((x) => x.id === id);
  return {
    title: m ? `${m.name} × ${challenge} — mager-bench` : "trace — mager-bench",
    description: m
      ? `Full trace of ${m.name} on the ${challenge} challenge: raw response, judge scores, and notes for every run.`
      : undefined,
  };
}

function DimScores({ r }: { r: Pick<RunDetail, "correctness" | "quality" | "documentation" | "speed_ms"> }) {
  return (
    <div className="flex flex-wrap gap-x-6 gap-y-1.5 text-sm text-fg-dim">
      <span className="inline-flex items-center gap-1.5">
        <span className={`h-1.5 w-1.5 rounded-full ${DIMENSION_STYLE.correctness.dot}`} />
        correctness{" "}
        <b className={`font-semibold ${DIMENSION_STYLE.correctness.text}`}>
          {r.correctness.toFixed(1)}
        </b>
      </span>
      <span className="inline-flex items-center gap-1.5">
        <span className={`h-1.5 w-1.5 rounded-full ${DIMENSION_STYLE.quality.dot}`} />
        quality{" "}
        <b className={`font-semibold ${DIMENSION_STYLE.quality.text}`}>{r.quality.toFixed(1)}</b>
      </span>
      <span className="inline-flex items-center gap-1.5">
        <span className={`h-1.5 w-1.5 rounded-full ${DIMENSION_STYLE.documentation.dot}`} />
        documentation{" "}
        <b className={`font-semibold ${DIMENSION_STYLE.documentation.text}`}>
          {r.documentation.toFixed(1)}
        </b>
      </span>
      <span>{r.speed_ms}ms</span>
    </div>
  );
}

export default async function TracePage({
  params,
}: {
  params: Promise<{ id: string; challenge: string }>;
}) {
  const { id, challenge: challengeName } = await params;
  const model = data.models.find((m) => m.id === id);
  const result = model?.challenges.find((c) => c.name === challengeName);
  if (!model || !result) return notFound();

  const def = challenges.find((c) => c.name === challengeName);
  const t = tier(result.total);
  const runs =
    result.run_details && result.run_details.length > 0
      ? result.run_details
      : [
          {
            run: 1,
            correctness: result.correctness,
            quality: result.quality,
            documentation: result.documentation,
            total: result.total,
            speed_ms: result.speed_ms,
            notes: result.notes,
            response: "",
          },
        ];

  return (
    <div className="px-4 py-10 sm:px-8 md:py-16">
      <div className="mx-auto flex max-w-3xl flex-col gap-10">
        <header className="rise flex flex-col gap-2 border-b border-amber-faint pb-5">
          <nav className="flex flex-wrap gap-x-4 text-xs text-fg-dim">
            <Link href={`/models/${model.id}`} className="hover:text-amber-bright">
              ← {model.name} runs
            </Link>
            <Link href={`/challenges/${result.name}`} className="hover:text-amber-bright">
              challenge spec →
            </Link>
          </nav>
          <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
            <h1 className="glow font-display text-3xl tracking-wide text-amber sm:text-4xl">
              {model.name} × {result.name}
            </h1>
            <span className={`font-display text-5xl ${t.text} ${t.glow}`}>
              {result.total.toFixed(1)}
              {result.stddev != null && result.stddev > 0 && (
                <span className="ml-1 font-mono text-sm text-fg-dim">±{result.stddev}</span>
              )}
            </span>
          </div>
          <p className="max-w-xl text-sm leading-relaxed text-fg">{result.description}</p>
          <DimScores r={result} />
        </header>

        {def && (
          <section className="rise flex flex-col gap-2" style={{ animationDelay: "80ms" }}>
            <details className="border border-amber-faint bg-bg-raised/40">
              <summary className="flex cursor-pointer items-center gap-2 px-4 py-2 text-xs text-fg-dim hover:text-amber-bright">
                <span className="h-2.5 w-2.5 rounded-full bg-alert/70" />
                <span className="h-2.5 w-2.5 rounded-full bg-amber/70" />
                <span className="h-2.5 w-2.5 rounded-full bg-green/70" />
                <span className="ml-2">$ cat {result.name}.prompt — what the model was asked</span>
              </summary>
              <pre className="overflow-x-auto whitespace-pre-wrap border-t border-amber-faint px-4 py-4 text-sm leading-relaxed text-fg">
{def.prompt}
              </pre>
            </details>
          </section>
        )}

        {runs.map((r, i) => {
          const rt = tier(r.total);
          return (
            <section
              key={r.run}
              className="rise flex flex-col gap-3"
              style={{ animationDelay: `${140 + i * 60}ms` }}
            >
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <h2 className="text-xs uppercase tracking-[0.3em] text-fg-dim">
                  run {r.run} of {runs.length}
                </h2>
                <span className={`font-display text-2xl ${rt.text} ${rt.glow}`}>
                  {r.total.toFixed(1)}
                </span>
              </div>
              <DimScores r={r} />
              {r.notes && (
                <p className="bg-bg/50 px-3 py-2 text-sm leading-relaxed text-fg">
                  <span className="text-amber-dim"># judge: </span>
                  {r.notes}
                </p>
              )}
              {r.response ? (
                <div className="border border-amber-faint bg-bg-raised/40">
                  <div className="flex items-center gap-2 border-b border-amber-faint px-4 py-2 text-xs text-fg-dim">
                    <span className="h-2.5 w-2.5 rounded-full bg-alert/70" />
                    <span className="h-2.5 w-2.5 rounded-full bg-amber/70" />
                    <span className="h-2.5 w-2.5 rounded-full bg-green/70" />
                    <span className="ml-2">
                      $ cat {model.id}.{result.name}.r{r.run}.response
                    </span>
                  </div>
                  <pre className="max-h-[36rem] overflow-auto whitespace-pre-wrap px-4 py-4 text-xs leading-relaxed text-fg">
{r.response}
                  </pre>
                </div>
              ) : (
                <p className="text-sm text-fg-dim">
                  No raw response stored for this run — re-run the bench with the latest CLI to
                  capture full traces.
                </p>
              )}
            </section>
          );
        })}
      </div>
    </div>
  );
}
