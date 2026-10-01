"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BallMark } from "@/components/court-mark";
export function SiteHeader() {
  const path = usePathname();
  return (
    <header className="site-header">
      <div className="site-width header-inner">
        <Link href="/" className="wordmark" aria-label="mager-bench home">
          <BallMark />
          mager-bench<span className="version-pill">v1.1</span>
        </Link>
        <nav className="main-nav" aria-label="Main navigation">
          <Link
            href="/#models"
            aria-current={
              path === "/" || path.startsWith("/models") ? "page" : undefined
            }
          >
            Models
          </Link>
          <Link
            href="/challenges"
            aria-current={path.startsWith("/challenges") ? "page" : undefined}
          >
            Challenges
          </Link>
          <Link
            href="/runs"
            aria-current={path.startsWith("/runs") ? "page" : undefined}
          >
            Run log
          </Link>
          <Link
            href="/archive"
            aria-current={path.startsWith("/archive") ? "page" : undefined}
          >
            Archives
          </Link>
          <a className="nav-source" href="https://github.com/mager/mager-bench">
            Source ↗
          </a>
        </nav>
      </div>
    </header>
  );
}
