import Link from "next/link";
export function SiteFooter() {
  return (
    <footer className="bench-footer bench-shell">
      <p>
        Built by <a href="https://mager.co">Mager</a>.
      </p>
      <nav aria-label="Footer">
        <Link href="/#method">How it works</Link>
        <a href="/api/v1.2/results">Download data</a>
      </nav>
    </footer>
  );
}
