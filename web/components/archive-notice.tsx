import Link from "next/link";
export function ArchiveNotice() {
  return (
    <div className="archive-notice">
      <div className="site-width">
        <strong>Historical results</strong> · Original thirteen-task suite ·
        LLM-judged scores out of 10.{" "}
        <Link href="/">Go to Counterexample Lab 1.1 →</Link>
      </div>
    </div>
  );
}
