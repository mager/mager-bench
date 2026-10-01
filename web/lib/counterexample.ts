import data from "@/data/counterexample.json";

export type LedgerOutput = {
  status?: string;
  balances?: Record<string, number>;
  revisions?: Record<string, number>;
};
export type LedgerEvent = {
  op: string;
  id?: string;
  from?: string;
  to?: string;
  amount?: number;
  expected_revision?: number;
};
export type Demo = {
  id: string;
  title: string;
  mutant: string;
  description: string;
  explanation: string;
  steps: {
    label: string;
    event: LedgerEvent;
    expected: LedgerOutput;
    actual: LedgerOutput;
    state: LedgerOutput;
    faultyState: LedgerOutput;
    differs: boolean;
  }[];
};
export type Run = {
  id: string;
  model: string;
  modelName: string;
  generated_at: string;
  reasoning_effort: string;
  status: string;
  response: string;
  error?: string;
  subject_elapsed_ms: number;
  score: null | {
    events_used: number;
    valid_traces: number;
    total_traces: number;
    killed: number;
    total_mutants: number;
    killed_mutants: string[];
    surviving_mutants: string[];
    trace_results: {
      index: number;
      oracle_match: boolean;
      first_mismatch: unknown;
      killed_mutants: string[];
    }[];
  };
};
export type LabData = {
  version: string;
  suiteHash: string;
  lastRunAt: string | null;
  calibrationReady: boolean;
  prompt: string;
  faults: { id: string; name: string; description: string; family: string }[];
  demos: Demo[];
  runs: Run[];
  models: {
    id: string;
    name: string;
    effort: string;
    attempts: number;
    completed: number;
    failed: number;
    scores: number[];
    runIds: string[];
    faultCoverage: Record<string, number>;
  }[];
};
export const lab = data as LabData;
export const sourceRoot = "https://github.com/mager/mager-bench";
export function dateLabel(iso: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "America/Chicago",
  }).format(new Date(iso));
}
export function pretty(value: unknown) {
  return JSON.stringify(value, null, 2);
}
