import Link from "next/link";
import resultsData from "@/data/results.json";
import challengesData from "@/data/challenges.json";
import { modelHref } from "@/lib/model-path";

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
  avg_correctness?: number;
  avg_quality?: number;
  avg_documentation?: number;
  avg_speed_ms: number;
  avg_stddev?: number | null;
  runs?: number;
  challenges: Challenge[];
};

type ChallengeDef = {
  name: string;
  description: string;
};

const data = resultsData as {
  generated_at: string;
  judge: string;
  judges?: string[];
  runs?: number;
  models: ModelResult[];
};

const challengeDefs = challengesData as ChallengeDef[];

function formatDate(iso: string) {
  return new Date(iso).toUTCString().replace("GMT", "UTC");
}

type Tier = "green" | "yellow" | "red";

function scoreTier(score: number): Tier {
  if (score > 9.5) return "green";
  if (score >= 7) return "yellow";
  return "red";
}

const TIER_STYLE: Record<Tier, { dot: string; text: string; glow: string }> = {
  green: { dot: "bg-green", text: "text-green", glow: "glow-green" },
  yellow: { dot: "bg-amber", text: "text-amber", glow: "glow" },
  red: { dot: "bg-alert", text: "text-alert", glow: "glow-alert" },
};

const COST_TIER_STYLE: Record<string, string> = {
  subscription: "text-cyan",
  free: "text-green",
  cheap: "text-cyan",
  paid: "text-magenta",
  unknown: "text-fg-dim",
};

export default function Home() {
  const models = data.models;
  const top = models[0];
  const challengeCount = challengeDefs.length;

  const boardAvg = (name: string) => {
    const scores = models
      .map((m) => m.challenges.find((c) => c.name === name)?.total)
      .filter((s): s is number => s != null);
    if (scores.length === 0) return null;
    return {
      avg: scores.reduce((a, b) => a + b, 0) / scores.length,
      n: scores.length,
    };
  };

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
            Thirteen coding tasks, run through headless Codex with a ChatGPT subscription
            and scored on{" "}
            <span className="font-semibold text-green">correctness</span>,{" "}
            <span className="font-semibold text-magenta">code quality</span>, and{" "}
            <span className="font-semibold text-cyan">documentation</span>.
          </p>
        </header>

        {top && (
          <section
            className="rise flex flex-col gap-5 border border-amber-faint bg-bg-raised/40 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6"
            style={{ animationDelay: "80ms" }}
          >
            <div className="crt-flicker">
              <h2 className="text-xs uppercase tracking-[0.3em] text-amber-bright">
                #01 / {top.name}
              </h2>
              <div className={`font-display text-[6.5rem] leading-none sm:text-[9rem] ${TIER_STYLE[scoreTier(top.average)].text} ${TIER_STYLE[scoreTier(top.average)].glow}`}>
                {top.average.toFixed(1)}
              </div>
              <p className="text-sm uppercase tracking-[0.2em] text-fg-dim">
                / 10 · {top.challenges.length}/{challengeCount} challenges
              </p>
            </div>
            <div className="max-w-xs space-y-3 text-sm leading-relaxed text-fg">
              <p>
                The current board uses one ChatGPT-signed-in judge:
                {" "}<span className="text-amber-bright">GPT-5.6 Sol through Codex CLI</span>.
              </p>
              <p className="text-fg-dim">
                Each subject ran in a fresh, read-only Codex session. Sol also grades its
                own run; read the full answers and verdicts before treating small gaps as meaningful.
              </p>
              <Link href={modelHref(top.id)} className="inline-block text-amber hover:text-amber-bright">
                inspect the leading run →
              </Link>
            </div>
          </section>
        )}

        <section id="leaderboard" className="rise scroll-mt-6" style={{ animationDelay: "140ms" }}>
          <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
            <h2 className="text-xs uppercase tracking-[0.3em] text-fg-dim">
              ChatGPT subscription leaderboard
            </h2>
            <span className="text-xs text-fg-dim">{models.length} models · {formatDate(data.generated_at)}</span>
          </div>
          <p className="mb-3 text-sm text-fg-dim">
            GPT-6 Astra and GPT-5.6 Sol share the same Sol judge. The older Sonnet 5 results
            are preserved in the{" "}
            <Link href="/archive/sonnet-5" className="text-amber hover:text-amber-bright">archive</Link>.
          </p>
          <div className="overflow-x-auto border border-amber-faint">
            <table className="w-full min-w-[720px] border-collapse text-sm">
              <thead>
                <tr className="border-b border-amber-faint text-left text-xs uppercase tracking-wider text-fg-dim">
                  <th className="px-4 py-3 font-normal">#</th>
                  <th className="px-4 py-3 font-normal">model</th>
                  <th className="px-4 py-3 font-normal">access</th>
                  <th
                    className="px-4 py-3 text-right font-normal"
                    title="average correctness · quality · documentation"
                  >
                    <span className="text-green">crct</span>{" "}
                    <span className="text-fg-dim">·</span>{" "}
                    <span className="text-magenta">qual</span>{" "}
                    <span className="text-fg-dim">·</span>{" "}
                    <span className="text-cyan">docs</span>
                  </th>
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
                        <Link
                          href={modelHref(m.id)}
                          className="inline-flex items-center gap-2 hover:text-amber-bright"
                        >
                          <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
                          {m.name}
                          <span className="text-xs text-amber-dim">→</span>
                        </Link>
                      </td>
                      <td className={`px-4 py-3 text-xs uppercase tracking-wider ${COST_TIER_STYLE[cost] ?? COST_TIER_STYLE.unknown}`}>
                        {cost}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-right tabular-nums">
                        {m.avg_correctness != null ? (
                          <>
                            <span className="text-green">{m.avg_correctness.toFixed(1)}</span>
                            <span className="text-fg-dim"> · </span>
                            <span className="text-magenta">{m.avg_quality?.toFixed(1)}</span>
                            <span className="text-fg-dim"> · </span>
                            <span className="text-cyan">{m.avg_documentation?.toFixed(1)}</span>
                          </>
                        ) : (
                          <span className="text-fg-dim">—</span>
                        )}
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
            <span className="text-green">crct</span> · <span className="text-magenta">qual</span> ·{" "}
            <span className="text-cyan">docs</span> are the rubric dimensions averaged across all{" "}
            {challengeCount} challenges — the headline average hides whether a model is
            correct-but-undocumented or well-written-but-wrong.
          </p>
          <p className="mt-2 text-xs text-fg-dim">
            click a model for its full challenge breakdown, raw responses, and judge notes.
            each published result comes from a saved headless Codex run.
          </p>
        </section>

        <section id="challenges" className="rise scroll-mt-6" style={{ animationDelay: "200ms" }}>
          <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
            <h2 className="text-xs uppercase tracking-[0.3em] text-fg-dim">
              the {challengeCount} challenges
            </h2>
            <Link
              href="/challenges"
              className="text-xs text-amber hover:text-amber-bright"
            >
              full specs + rubrics →
            </Link>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {challengeDefs.map((c) => {
              const board = boardAvg(c.name);
              const style = board ? TIER_STYLE[scoreTier(board.avg)] : null;
              return (
                <Link
                  key={c.name}
                  href={`/challenges/${c.name}`}
                  className="lift group flex flex-col gap-1.5 border border-amber-faint bg-bg-raised/40 px-4 py-3"
                >
                  <div className="flex items-baseline justify-between gap-3">
                    <span className="font-mono text-sm font-semibold tracking-wide text-amber-bright group-hover:text-amber">
                      {c.name}
                      <span className="ml-1.5 inline-block text-amber-dim transition-transform group-hover:translate-x-0.5">
                        →
                      </span>
                    </span>
                    {board && style && (
                      <span
                        className={`font-display text-xl ${style.text}`}
                        title={`board average across ${board.n} model${board.n === 1 ? "" : "s"}`}
                      >
                        {board.avg.toFixed(1)}
                      </span>
                    )}
                  </div>
                  <p className="text-sm leading-relaxed text-fg">{c.description}</p>
                </Link>
              );
            })}
          </div>
          <p className="mt-2 text-xs text-fg-dim">
            score shown is the board average across all {models.length} scored models — a rough
            difficulty read. every model attempts every challenge.
          </p>
        </section>

        <section
          className="rise border border-amber-faint bg-bg-raised/40 px-4 py-4"
          style={{ animationDelay: "260ms" }}
        >
          <h2 className="mb-2 text-xs uppercase tracking-[0.3em] text-fg-dim">
            methodology, honestly
          </h2>
          <p className="text-sm leading-relaxed text-fg">
            Every score here uses <span className="font-semibold text-amber-bright">{data.judge}</span>.
            The judge is also a subject on this board, so self-judging bias is possible.
            Codex CLI prompts for an output length but does not enforce the API token cap.
            Every model page links to its full response and judge notes. The earlier API runs
            remain in the <Link href="/archive/sonnet-5" className="text-amber hover:text-amber-bright">Sonnet 5 archive</Link>.
          </p>
        </section>

        <section
          id="api"
          className="rise scroll-mt-6 border border-amber-faint bg-bg-raised/40 px-4 py-4 text-xs"
          style={{ animationDelay: "280ms" }}
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
