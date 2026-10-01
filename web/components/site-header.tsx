"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function SiteHeader() {
  const pathname = usePathname();
  const isCurrentChallenge =
    pathname === "/challenges" ||
    pathname === "/challenges/counterexample-ledger";
  const links = [
    { href: "/", label: "Overview", active: pathname === "/" },
    { href: "/challenges", label: "The test", active: isCurrentChallenge },
    { href: "/runs", label: "Runs", active: pathname.startsWith("/runs") },
    {
      href: "/archive",
      label: "Archive",
      active:
        pathname.startsWith("/archive") ||
        pathname.startsWith("/models") ||
        (pathname.startsWith("/challenges/") && !isCurrentChallenge),
    },
  ];
  return (
    <header className="site-header">
      <div className="site-width header-inner">
        <Link href="/" className="wordmark" aria-label="mager-bench home">
          <span className="brand-mark" aria-hidden="true">
            <i />
            <i />
            <i />
          </span>
          mager-bench
          <span className="version-pill">v1.1</span>
        </Link>
        <nav aria-label="Main navigation" className="main-nav">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              aria-current={link.active ? "page" : undefined}
            >
              {link.label}
            </Link>
          ))}
          <a className="nav-source" href="https://github.com/mager/mager-bench">
            GitHub ↗
          </a>
        </nav>
      </div>
    </header>
  );
}
