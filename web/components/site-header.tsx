"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_LINKS = [
  { href: "/", label: "leaderboard" },
  { href: "/challenges", label: "challenges" },
  { href: "/fund", label: "fund the bench" },
];

export function SiteHeader() {
  const pathname = usePathname();
  return (
    <header className="border-b border-amber-faint px-4 sm:px-8">
      <div className="mx-auto flex max-w-4xl flex-wrap items-baseline justify-between gap-x-4 gap-y-1 py-3">
        <Link
          href="/"
          className="glow font-display text-xl tracking-wide text-amber hover:text-amber-bright"
        >
          mager-bench
        </Link>
        <nav aria-label="site" className="flex flex-wrap items-baseline gap-x-5 gap-y-1 text-xs">
          {NAV_LINKS.map((link) => {
            const active =
              link.href === "/" ? pathname === "/" : pathname.startsWith(link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                aria-current={active ? "page" : undefined}
                className={
                  active
                    ? "text-amber-bright underline decoration-dotted underline-offset-4"
                    : "text-fg-dim hover:text-amber-bright"
                }
              >
                {link.label}
              </Link>
            );
          })}
          <a className="text-fg-dim hover:text-amber-bright" href="/#api">
            api
          </a>
          <a
            className="text-fg-dim hover:text-amber-bright"
            href="https://github.com/mager/mager-bench"
            target="_blank"
            rel="noreferrer"
          >
            source →
          </a>
        </nav>
      </div>
    </header>
  );
}
