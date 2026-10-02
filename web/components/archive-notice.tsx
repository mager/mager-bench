"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
export function ArchiveNotice() {
  const p = usePathname();
  if (
    !p.startsWith("/models/") &&
    !p.startsWith("/challenges") &&
    !p.startsWith("/runs/") &&
    !p.startsWith("/archive/")
  )
    return null;
  return (
    <aside className="bench-shell quiet" style={{ paddingBlock: 16 }}>
      <strong>Historical benchmark.</strong> These results retain their original
      scoring rules.{" "}
      <Link className="bench-link" href="/">
        View the active v1.2 suite
      </Link>
      .
    </aside>
  );
}
