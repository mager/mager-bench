import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="site-width footer-inner">
        <p>
          <strong className="text-fg">mager-bench</strong> · Small tests.
          Inspectable evidence.
        </p>
        <nav aria-label="Footer">
          <Link href="/challenges#method">Methodology</Link>
          <a href="/api/v1.1/results">Data API</a>
          <a href="https://github.com/mager/mager-bench">Source ↗</a>
        </nav>
      </div>
    </footer>
  );
}
