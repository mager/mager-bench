import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const [runArg, boardArg = "results.json"] = process.argv.slice(2);
if (!runArg) {
  throw new Error("Usage: node web/scripts/merge-subscription-run.mjs runs/<run>.json [board.json]");
}

const runPath = path.resolve(root, runArg);
const boardPath = path.resolve(root, boardArg);
if (runPath === boardPath) throw new Error("Run and board paths must differ");

const run = JSON.parse(readFileSync(runPath, "utf8"));
const expected = "codex-cli/gpt-5.6-sol";
const challenges = JSON.parse(readFileSync(path.join(root, "web/data/challenges.json"), "utf8"));
const names = new Set(challenges.map((challenge) => challenge.name));
const rows = run.results ?? [];
const models = new Set(rows.map((row) => row.model));
const seen = new Set();

if (run.judge !== expected || run.runs !== 1 || models.size !== 1 ||
    rows.length !== names.size ||
    rows.some((row) => {
      const key = `${row.model}/${row.challenge}`;
      if (seen.has(key)) return true;
      seen.add(key);
      return !names.has(row.challenge) || row.judge !== expected ||
        !row.model.startsWith("codex-cli/") || !row.response?.trim() ||
        /judge error/i.test(row.notes ?? "") ||
        ["correctness", "quality", "documentation", "total_score"].some(
          (field) => !Number.isFinite(row[field]) || row[field] < 0 || row[field] > 10
        ) ||
        Math.abs(row.total_score -
          Math.round((row.correctness + row.quality + row.documentation) / 3 * 10) / 10) > 0.11;
    })) {
  throw new Error("Run failed subscription-board integrity checks");
}

const board = existsSync(boardPath)
  ? JSON.parse(readFileSync(boardPath, "utf8"))
  : { generated_at: "", judge: expected, results: [] };
if (board.judge !== expected || board.results.some((row) => row.judge !== expected)) {
  throw new Error(`Board judge must be ${expected}; archive the old board before switching`);
}

const model = [...models][0];
const retained = board.results.filter((row) => row.model !== model);
const merged = [...retained, ...rows];
writeFileSync(boardPath, JSON.stringify({
  generated_at: new Date().toISOString(),
  judge: expected,
  judges: [expected],
  runs: 1,
  tier: "subscription",
  results: merged,
}, null, 2) + "\n");
console.log(`Merged ${model}: ${rows.length} challenges; board now has ${new Set(merged.map((row) => row.model)).size} model(s)`);
