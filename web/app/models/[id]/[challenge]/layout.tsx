import { ArchiveNotice } from "@/components/archive-notice";
export default function TraceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <ArchiveNotice />
      {children}
    </>
  );
}
