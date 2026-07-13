import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import challengesData from "@/data/challenges.json";
import resultsData from "@/data/results.json";

type ChallengeDef = {
  name: string;
  description: string;
  prompt: string;
  rubric: { correctness: string; quality: string; documentation: string };
};

type ChallengeResult = {
  name: string;
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
  challenges: ChallengeResult[];
};

const challenges = challengesData as ChallengeDef[];
const results = resultsData as { models: ModelResult[] };

const DIMENSION_STYLE = {
  correctness: { dot: "bg-green", text: "text-green" },
  quality: { dot: "bg-magenta", text: "text-magenta" },
  documentation: { dot: "bg-cyan", text: "text-cyan" },
} as const;

export function generateStaticParams() {
  return challenges.map((c) => ({ slug: c.name }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const c = challenges.find((x) => x.name === slug);
  return { title: c ? `${c.name} — mager-bench` : "challenge — mager-bench" };
}

function tier(score: number) {
  if (score >= 8.5) return { text: "text-green", glow: "glow-green" };
  if (score >= 7) return { text: "text-amber", glow: "glow" };
  if (score >= 5) return { text: "text-amber-dim", glow: "" };
  return { text: "text-alert", glow: "glow-alert" };
}

export default async function ChallengePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const challenge = challenges.find((c) => c.name === slug);
  if (!challenge) return notFound();

  const rows = results.models
    .map((m) => {
      const c = m.challenges.find((x) => x.name === challenge.name);
      return c ? { model: m.name, ...c } : null;
    })
    .filter((x): x is ChallengeResult & { model: string } => x !== null)
    .sort((a, b) => b.total - a.total);

  return (
    <div className="min-h-screen px-4 py-10 sm:px-8 md:py-16">
      <div className="mx-auto flex max-w-3xl flex-col gap-10">
        <header className="rise flex flex-col gap-2 border-b border-amber-faint pb-5">
          <Link href="/challenges" className="text-xs text-amber-dim hover:text-amber-bright">
            ← all challenges
          </Link>
          <h1 className="glow font-display text-4xl tracking-wide sm:text-5xl">
            {challenge.name}
          </h1>
          <p className="max-w-xl text-sm leading-relaxed text-amber-dim">{challenge.description}</p>
        </header>

        <section className="rise flex flex-col gap-2" style={{ animationDelay: "80ms" }}>
          <h2 className="text-xs uppercase tracking-[0.3em] text-amber-dim">the prompt</h2>
          <div className="border border-amber-faint bg-bg-raised/40">
            <div className="flex items-center gap-2 border-b border-amber-faint px-4 py-2 text-xs text-amber-dim">
              <span className="h-2.5 w-2.5 rounded-full bg-alert/70" />
              <span className="h-2.5 w-2.5 rounded-full bg-amber/70" />
              <span className="h-2.5 w-2.5 rounded-full bg-green/70" />
              <span className="ml-2">$ cat {challenge.name}.prompt</span>
            </div>
            <pre className="overflow-x-auto whitespace-pre-wrap px-4 py-4 text-sm leading-relaxed text-amber">
{challenge.prompt}
            </pre>
          </div>
        </section>

        <section className="rise flex flex-col gap-3" style={{ animationDelay: "140ms" }}>
          <h2 className="text-xs uppercase tracking-[0.3em] text-amber-dim">rubric</h2>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {(["correctness", "quality", "documentation"] as const).map((dim) => (
              <div key={dim} className="border border-amber-faint bg-bg-raised/40 px-3 py-3">
                <div className="flex items-center gap-2">
                  <span className={`h-1.5 w-1.5 rounded-full ${DIMENSION_STYLE[dim].dot}`} />
                  <span className={`text-xs font-semibold uppercase tracking-wider ${DIMENSION_STYLE[dim].text}`}>
                    {dim}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-relaxed text-amber-dim">{challenge.rubric[dim]}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="rise flex flex-col gap-3" style={{ animationDelay: "200ms" }}>
          <h2 className="text-xs uppercase tracking-[0.3em] text-amber-dim">results</h2>
          {rows.length === 0 ? (
            <p className="text-sm text-amber-dim">No model has run this challenge yet.</p>
          ) : (
            <div className="flex flex-col gap-3">
              {rows.map((r) => {
                const t = tier(r.total);
                return (
                  <article key={r.model} className="lift border border-amber-faint bg-bg-raised/40 px-4 py-4">
                    <div className="flex items-center gap-3">
                      <h3 className="font-mono text-sm font-semibold tracking-wide text-amber-bright">
                        {r.model}
                      </h3>
                      <div
                        className="h-px flex-1"
                        style={{
                          backgroundImage:
                            "repeating-linear-gradient(to right, var(--amber-dim) 0, var(--amber-dim) 4px, transparent 4px, transparent 8px)",
                        }}
                      />
                      <span className={`font-display text-2xl ${t.text} ${t.glow}`}>
                        {r.total.toFixed(1)}
                      </span>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-x-6 gap-y-1.5 text-sm text-amber-dim">
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
                        <b className={`font-semibold ${DIMENSION_STYLE.quality.text}`}>
                          {r.quality.toFixed(1)}
                        </b>
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
                    <p className="mt-3 bg-bg/50 px-3 py-2 text-sm leading-relaxed text-amber">
                      <span className="text-amber-dim"># </span>
                      {r.notes}
                    </p>
                  </article>
                );
              })}
            </div>
          )}
        </section>

        <footer className="rise flex items-center justify-between border-t border-amber-faint pt-4 text-xs text-amber-dim">
          <Link href="/challenges" className="hover:text-amber-bright">
            ← all challenges
          </Link>
          <Link href="/" className="hover:text-amber-bright">
            leaderboard →
          </Link>
        </footer>
      </div>
    </div>
  );
}
