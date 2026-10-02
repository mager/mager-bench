"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
export function SiteHeader() {
  const path = usePathname();
  return (
    <header className="bench-header">
      <div className="bench-shell bench-nav">
        <Link href="/" className="bench-wordmark" aria-label="mager-bench home">
          mager-bench<span>1.2</span>
        </Link>
        <nav aria-label="Main navigation">
          <Link href="/#tasks">The tasks</Link>
          <Link
            href="/runs"
            aria-current={path === "/runs" ? "page" : undefined}
          >
            Runs
          </Link>
          <Link
            href="/archive"
            aria-current={path.startsWith("/archive") ? "page" : undefined}
          >
            Archive
          </Link>
          <a href="https://github.com/mager/mager-bench" className="source-nav">
            GitHub
          </a>
        </nav>
      </div>
    </header>
  );
}
