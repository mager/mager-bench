import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Funding archive — mager-bench",
  description: "The former API funding drive is archived. Current benchmark runs use a ChatGPT subscription.",
};

export default function FundPage() {
  return (
    <main className="min-h-screen px-4 py-10 sm:px-8 md:py-16">
      <div className="mx-auto flex max-w-4xl flex-col gap-9">
        <header className="border-b border-amber-faint pb-6">
          <Link href="/" className="text-xs text-fg-dim hover:text-amber-bright">← current leaderboard</Link>
          <p className="mt-6 text-xs uppercase tracking-[0.25em] text-amber-dim">former API-era plan</p>
          <h1 className="mt-2 font-display text-4xl text-amber sm:text-5xl">Funding drive archived</h1>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-fg">
            New mager-bench runs use headless Codex with a local ChatGPT subscription.
            The earlier API-cost funding drive and model wishlist are no longer active.
          </p>
        </header>
        <p className="text-sm leading-relaxed text-fg-dim">
          The original API results remain available in the{" "}
          <Link href="/archive/sonnet-5" className="text-amber hover:text-amber-bright">Sonnet 5 board archive</Link>.
          Every new score on the <Link href="/" className="text-amber hover:text-amber-bright">current board</Link> comes
          from a saved ChatGPT-signed-in Codex run.
        </p>
      </div>
    </main>
  );
}
