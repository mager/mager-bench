/**
 * Deep links into the Arize AX UI for bench-run traces.
 *
 * Links render only when the three NEXT_PUBLIC_ARIZE_* env vars are set
 * (org, space, and project IDs — base64 values copied from the Arize
 * browser URL: app.arize.com/organizations/{org}/spaces/{space}/projects/{project}).
 */

const ORG = process.env.NEXT_PUBLIC_ARIZE_ORG_ID;
const SPACE = process.env.NEXT_PUBLIC_ARIZE_SPACE_ID;
const PROJECT = process.env.NEXT_PUBLIC_ARIZE_PROJECT_ID;

const DAY_MS = 24 * 60 * 60 * 1000;

export function arizeTraceUrl(
  traceId: string | null | undefined,
  generatedAt: string,
): string | null {
  if (!traceId || !ORG || !SPACE || !PROJECT) return null;
  const anchor = Date.parse(generatedAt) || Date.now();
  // ±1 day around the run — Arize shows "no data" if the trace falls
  // outside the linked time window
  const params = new URLSearchParams({
    selectedTraceId: traceId,
    queryFilterA: "",
    selectedTab: "llmTracing",
    timeZoneA: "America/Chicago",
    startA: String(anchor - DAY_MS),
    endA: String(anchor + DAY_MS),
    envA: "tracing",
    modelType: "generative_llm",
  });
  return `https://app.arize.com/organizations/${ORG}/spaces/${SPACE}/projects/${PROJECT}?${params}`;
}
