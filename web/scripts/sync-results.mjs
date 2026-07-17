import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const raw = JSON.parse(readFileSync(path.join(__dirname, "../../results.json"), "utf8"));

const DESCRIPTIONS = {
  fizzbuzz: "Baseline correctness + code style",
  "binary-search": "Algorithm + full docstring (Args/Returns/Raises + examples)",
  "api-client": "Class design + error handling + type hints + docs",
  "readme-writer": "Pure documentation ability — no code at all",
  refactor: "Code clarity + whether the model can explain its changes",
  "test-writing": "Edge-case thinking + pytest parametrize discipline",
  debug: "Careful reading + correctness reasoning over broken code",
  "async-fetch": "Async concurrency patterns + retry/timeout handling",
  sql: "CTE + window function fluency on a real schema",
  "go-test": "Idiomatic Go table-driven tests + benchmark",
  "elixir-test": "ExUnit describe blocks + assert_raise + unicode handling",
  doom: "DDA raycaster + textures + door + minimap + Z-buffer — the signature challenge",
};

const DISPLAY_NAMES = {
  "claude-haiku-4-5": "Claude Haiku 4.5",
  "claude-sonnet-5": "Claude Sonnet 5",
  "claude-sonnet-4-6": "Claude Sonnet 4.6",
  "claude-opus-4-8": "Claude Opus 4.8",
  "gpt-4o": "GPT-4o",
  "gpt-4o-mini": "GPT-4o mini",
  "gemini-2.0-flash": "Gemini 2.0 Flash",
  "gemini-2.5-pro": "Gemini 2.5 Pro",
};

const byModel = new Map();
for (const r of raw.results) {
  if (!byModel.has(r.model)) byModel.set(r.model, []);
  byModel.get(r.model).push(r);
}

const models = [...byModel.entries()]
  .map(([id, challenges]) => {
    const average = challenges.reduce((sum, c) => sum + c.total_score, 0) / challenges.length;
    const avgSpeedMs = Math.round(
      challenges.reduce((sum, c) => sum + c.speed_ms, 0) / challenges.length
    );
    return {
      id,
      name: DISPLAY_NAMES[id] ?? id,
      average: Math.round(average * 10) / 10,
      avg_speed_ms: avgSpeedMs,
      challenges: challenges
        .sort((a, b) => b.total_score - a.total_score)
        .map((c) => ({
          name: c.challenge,
          description: DESCRIPTIONS[c.challenge] ?? "",
          correctness: c.correctness,
          quality: c.quality,
          documentation: c.documentation,
          total: c.total_score,
          speed_ms: c.speed_ms,
          notes: c.notes,
        })),
    };
  })
  .sort((a, b) => b.average - a.average);

const out = {
  generated_at: raw.generated_at,
  judge: raw.judge,
  models,
};

mkdirSync(path.join(__dirname, "../data"), { recursive: true });
writeFileSync(path.join(__dirname, "../data/results.json"), JSON.stringify(out, null, 2) + "\n");
console.log(`wrote data/results.json (${models.length} model${models.length === 1 ? "" : "s"})`);
