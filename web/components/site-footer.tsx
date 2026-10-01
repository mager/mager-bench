import Link from "next/link";
export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="site-width footer-inner">
        <p>
          <strong>mager-bench</strong> · Everybody’s got something to prove.
        </p>
        <nav aria-label="Footer">
          <Link href="/challenges#scoring">Scoring rules</Link>
          <a href="/api/v1.1/results">Data</a>
          <a href="https://github.com/mager/mager-bench">Source ↗</a>
        </nav>
      </div>
    </footer>
  );
}
