export function CourtMark({ className = "" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 420 270"
      fill="none"
      aria-hidden="true"
    >
      <path d="M24 244V26h372v218H24Z" stroke="currentColor" strokeWidth="2" />
      <path
        d="M210 26v218M210 90a45 45 0 0 1 0 90 45 45 0 0 1 0-90Z"
        stroke="currentColor"
        strokeWidth="2"
      />
      <path
        d="M24 77h77v116H24m0-138h25a103 103 0 0 1 0 160H24M396 77h-77v116h77m0-138h-25a103 103 0 0 0 0 160h25"
        stroke="currentColor"
        strokeWidth="2"
      />
      <path
        d="M101 102a33 33 0 0 1 0 66m218-66a33 33 0 0 0 0 66M39 115v40m342-40v40"
        stroke="currentColor"
        strokeWidth="2"
      />
      <circle cx="48" cy="135" r="8" stroke="currentColor" strokeWidth="2" />
      <circle cx="372" cy="135" r="8" stroke="currentColor" strokeWidth="2" />
      <path d="M155 257h110m-98 6h86" stroke="currentColor" strokeWidth="4" />
    </svg>
  );
}
export function BallMark() {
  return (
    <svg viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <circle
        cx="16"
        cy="16"
        r="13.5"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <path
        d="M2.5 16h27M16 2.5v27M6 7c13 2 13 16 0 18M26 7c-13 2-13 16 0 18"
        stroke="currentColor"
        strokeWidth="1.6"
      />
    </svg>
  );
}
