import Link from "next/link";
import type { Metadata } from "next";
import challengesData from "@/data/challenges.json";
import resultsData from "@/data/results.json";

export const metadata: Metadata = {
  title: "challenges — mager-bench",
  description: "Every mager-bench challenge: the exact prompt, the rubric, and how models scored.",
};

type ChallengeDef = {
  name: string;
  description: string;
  prompt: string;
  rubric: { correctness: string; quality: string; documentation: string };
};

type ModelResult = {
  id: string;
  name: string;
  challenges: { name: string; total: number }[];
};

const challenges = challengesData as ChallengeDef[];
const results = resultsData as { models: ModelResult[] };

function topScoreFor(name: string) {
  let best: { model: string; total: number } | null = null;
  for (const m of results.models) {
    const c = m.challenges.find((x) => x.name === name);
    if (c && (!best || c.total > best.total)) best = { model: m.name, total: c.total };
  }
  return best;
}

export default function ChallengesIndex() {
  return (
    <div className="min-h-screen px-4 py-10 sm:px-8 md:py-16">
      <div className="mx-auto flex max-w-4xl flex-col gap-10">
        <header className="rise flex flex-col gap-2 border-b border-amber-faint pb-5">
          <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
            <h1 className="glow font-display text-4xl tracking-wide text-amber sm:text-5xl">
              challenges
            </h1>
            <Link href="/" className="text-xs text-fg-dim hover:text-amber-bright">
              ← leaderboard
            </Link>
          </div>
          <p className="max-w-xl text-sm leading-relaxed text-fg">
            The five tasks every model runs. Full prompt, full rubric, no black box — click
            into any of them to see exactly what&apos;s being judged.
          </p>
        </header>

        <div className="rise grid grid-cols-1 gap-4 sm:grid-cols-2" style={{ animationDelay: "80ms" }}>
          {challenges.map((c, i) => {
            const best = topScoreFor(c.name);
            return (
              <Link
                key={c.name}
                href={`/challenges/${c.name}`}
                className="lift group flex flex-col gap-2 border border-amber-faint bg-bg-raised/40 px-4 py-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <span className="text-xs text-fg-dim">{String(i + 1).padStart(2, "0")}</span>
                    <h2 className="font-mono text-base font-semibold tracking-wide text-amber-bright group-hover:text-amber">
                      {c.name}
                    </h2>
                  </div>
                  {best && (
                    <span
                      className={`font-display text-xl leading-none ${
                        best.total > 9.5
                          ? "text-green glow-green"
                          : best.total >= 7
                            ? "text-amber glow"
                            : "text-alert glow-alert"
                      }`}
                    >
                      {best.total.toFixed(1)}
                    </span>
                  )}
                </div>
                <p className="text-sm leading-relaxed text-fg-dim">{c.description}</p>
                <span className="mt-1 text-xs text-fg-dim">
                  {best ? (
                    <>
                      best so far: <span className="text-amber">{best.model}</span>
                    </>
                  ) : (
                    "no runs yet"
                  )}
                </span>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
