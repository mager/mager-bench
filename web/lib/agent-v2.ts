import data from "@/data/agent-v2.json";
export type Score = { passed: number; total: number };
export type Check = {
  id: string;
  group: string;
  input: unknown;
  expected: unknown;
  actual: unknown;
  error?: string;
};
export type Phase = {
  phase: number;
  status: string;
  error: string | null;
  elapsed_ms: number | null;
  usage: Record<string, number> | null;
  command_count: number | null;
  diff: string | null;
  sources: Record<string, string> | null;
  response: string | null;
  integrity_errors: string[] | null;
  score:
    | (Score & {
        groups: { contract: Score; generated: Score; regression?: Score };
        failures: Check[];
      })
    | null;
};
export type Run = {
  id: string;
  kind: "evaluation" | "preflight";
  model: string;
  reasoning_effort: string;
  seed: number;
  level: number;
  suite_sha256: string;
  generated_at: string;
  status: string;
  score: (Score & { tasks_passed: number; tasks_total: number }) | null;
  elapsed_ms: number;
  generation_ms: number;
  runtime: Record<string, string> | null;
  error: string | null;
  raw_url: string;
  tasks: { id: string; phases: Phase[] }[];
  probe: { stderr: string; error: string | null; elapsed_ms: number } | null;
};
type BenchData = {
  version: string;
  suite_sha256: string;
  phase_seconds: number;
  budget_seconds: number;
  checks: number;
  levels: Record<string, { entities: number; operations: number }>;
  tasks: {
    id: string;
    title: string;
    summary: string;
    phases: string[];
    prompts: string[];
    starter: Record<string, string>;
  }[];
  runs: Run[];
};
// Check the generated JSON's structure at compile time. Narrow its discriminator
// at runtime because TypeScript widens JSON string literals to `string`.
function checkedRun(run: Omit<Run, "kind"> & { kind: string }): Run {
  if (run.kind !== "evaluation" && run.kind !== "preflight") {
    throw new Error(`Unknown run kind: ${run.kind}`);
  }
  return { ...run, kind: run.kind };
}
export const agentBench: BenchData = {
  ...data,
  runs: data.runs.map(checkedRun),
};
export const evaluations = agentBench.runs.filter(
  (run) => run.kind === "evaluation",
);
export const modelName = (model: string) =>
  model
    .replace("codex-cli/", "")
    .replace(/^gpt-/, "GPT-")
    .replace(
      /-(sol|astra|luna|terra)$/,
      (_, name: string) => ` ${name[0].toUpperCase()}${name.slice(1)}`,
    );
export const duration = (ms: number) =>
  ms < 1000
    ? `${ms} ms`
    : ms < 60000
      ? `${(ms / 1000).toFixed(1)} s`
      : `${Math.floor(ms / 60000)}m ${Math.round((ms % 60000) / 1000)}s`;
export const resultLabel = (run: Run) =>
  run.kind === "preflight"
    ? run.status === "completed"
      ? "CLI check passed · unscored"
      : "CLI check failed · unscored"
    : run.score
      ? `${run.score.passed} / ${run.score.total} checks`
      : "Incomplete · unscored";
