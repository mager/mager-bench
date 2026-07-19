import Link from "next/link";
import challengesData from "@/data/challenges.json";
import resultsData from "@/data/results.json";

const challengeCount = (challengesData as unknown[]).length;
const results = resultsData as { judge: string; models: unknown[] };
const modelCount = results.models.length;

export function SiteFooter() {
  return (
    <footer className="border-t border-amber-faint px-4 sm:px-8">
      <div className="mx-auto flex max-w-4xl flex-col gap-2 py-5 text-xs text-fg-dim">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span>
            mager-bench // {challengeCount} challenges · {modelCount}{" "}
            {modelCount === 1 ? "model" : "models"} · judged by {results.judge}
          </span>
          <span className="cursor">AWAITING CHALLENGER</span>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <nav aria-label="footer" className="flex flex-wrap gap-x-5 gap-y-1">
            <Link className="hover:text-amber-bright" href="/">
              leaderboard
            </Link>
            <Link className="hover:text-amber-bright" href="/challenges">
              challenges
            </Link>
            <Link className="hover:text-amber-bright" href="/fund">
              fund the bench
            </Link>
            <a className="hover:text-amber-bright" href="/api/results">
              api
            </a>
            <a
              className="hover:text-amber-bright"
              href="https://github.com/mager/mager-bench"
              target="_blank"
              rel="noreferrer"
            >
              source →
            </a>
            <a
              className="hover:text-amber-bright"
              href="https://mager.co"
              target="_blank"
              rel="noreferrer"
            >
              mager.co →
            </a>
          </nav>
          <Link href="/challenges" className="hover:text-amber-bright">
            think a model can pass all {challengeCount}? →
          </Link>
        </div>
      </div>
    </footer>
  );
}
