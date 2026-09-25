import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const source = path.join(root, "runs/2026-09-25-codex-cli-gpt-5.6-sol-rescored.json");
const destination = path.join(root, "web/data/codex-cli-sol.json");
const run = JSON.parse(readFileSync(source, "utf8"));
const expected = "codex-cli/gpt-5.6-sol";

if (run.judge !== expected || run.results.length !== 13 ||
    new Set(run.results.map((row) => row.challenge)).size !== 13 ||
    run.results.some((row) => row.model !== expected || row.judge !== expected ||
      !row.response?.trim() || /judge error/i.test(row.notes))) {
  throw new Error("Codex CLI run failed the experiment data integrity check");
}

const rows = run.results.map((row) => ({
  challenge: row.challenge,
  correctness: row.correctness,
  quality: row.quality,
  documentation: row.documentation,
  total: row.total_score,
  speed_ms: row.speed_ms,
  notes: row.notes,
  response: row.response,
}));

const average = rows.reduce((sum, row) => sum + row.total, 0) / rows.length;
writeFileSync(destination, JSON.stringify({
  generated_at: run.generated_at,
  model: expected,
  judge: expected,
  average: Math.round(average * 10) / 10,
  rows,
}, null, 2) + "\n");
console.log(`Synced ${rows.length} Codex CLI results to web/data/codex-cli-sol.json`);
