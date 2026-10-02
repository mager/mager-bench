import data from "@/data/everyday.json";
export type Case = {
  label: string;
  input: unknown;
  expected: unknown;
  actual?: unknown;
  passed?: boolean;
  error?: string;
};
export type Task = {
  id: string;
  title: string;
  description: string;
  example: string;
  contract: string;
  prompt: string;
  cases: Case[];
};
export type TaskRun = {
  id: string;
  prompt: string;
  status: string;
  response: string;
  subject_elapsed_ms?: number;
  error?: string;
  score: { passed: number; total: number; cases: Case[] } | null;
};
export type Run = {
  id: string;
  model: string;
  generated_at: string;
  suite_sha256: string;
  reasoning_effort: string;
  status: string;
  elapsed_ms: number;
  artifact: string;
  error?: string;
  tasks: TaskRun[];
  score: { passed: number; total: number } | null;
};
export const everyday = data as unknown as {
  version: string;
  suiteHash: string;
  tasks: Task[];
  runs: Run[];
};
export const source = "https://github.com/mager/mager-bench";
export const modelName = (model: string) =>
  model
    .replace("codex-cli/", "")
    .replace("gpt-", "GPT-")
    .replace(/-sol$/, " Sol")
    .replace(/-astra$/, " Astra");
export const date = (value: string) =>
  new Date(value).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  });
