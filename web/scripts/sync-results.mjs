import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, "../..");
const rawPath = path.join(root, "results.json");
const fundingPath = path.join(__dirname, "../data/funding.json");

if (!existsSync(rawPath)) {
  console.error("missing ../../results.json — run: python bench.py --output results.json");
  process.exit(1);
}

const raw = JSON.parse(readFileSync(rawPath, "utf8"));

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
  slots: "Vegas slot machine — reels, pay table, betting, win animations",
};

const DISPLAY_NAMES = {
  "claude-haiku-4-5": "Claude Haiku 4.5",
  "claude-sonnet-5": "Claude Sonnet 5",
  "claude-sonnet-4-6": "Claude Sonnet 4.6",
  "claude-opus-4-8": "Claude Opus 4.8",
  "gpt-4o": "GPT-4o",
  "gpt-4o-mini": "GPT-4o mini",
  "gemini-2.0-flash": "Gemini 2.0 Flash",
  "gemini-2.5-flash": "Gemini 2.5 Flash",
  "gemini-2.5-pro": "Gemini 2.5 Pro",
  "llama-3.3-70b": "Llama 3.3 70B",
  "llama-3.1-8b": "Llama 3.1 8B",
};

const TIERS = {
  "llama-3.3-70b": "free",
  "llama-3.1-8b": "free",
  "gemini-2.0-flash": "free",
  "gemini-2.5-flash": "free",
  "claude-haiku-4-5": "cheap",
  "gpt-4o-mini": "cheap",
  "claude-sonnet-4-6": "paid",
  "claude-sonnet-5": "paid",
  "claude-opus-4-8": "paid",
  "gpt-4o": "paid",
  "gemini-2.5-pro": "paid",
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
    const stds = challenges.map((c) => c.stddev).filter((x) => typeof x === "number");
    const avgStd =
      stds.length > 0 ? Math.round((stds.reduce((a, b) => a + b, 0) / stds.length) * 100) / 100 : null;
    return {
      id,
      name: DISPLAY_NAMES[id] ?? id,
      tier: TIERS[id] ?? "unknown",
      average: Math.round(average * 10) / 10,
      avg_speed_ms: avgSpeedMs,
      avg_stddev: avgStd,
      runs: challenges[0]?.runs ?? raw.runs ?? 1,
      challenges: challenges
        .slice()
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
          stddev: c.stddev ?? null,
          runs: c.runs ?? 1,
          // per-run paper trail; older results.json files predate run_details,
          // so synthesize a single-run trace from the flat fields
          run_details:
            Array.isArray(c.run_details) && c.run_details.length > 0
              ? c.run_details
              : [
                  {
                    run: 1,
                    correctness: c.correctness,
                    quality: c.quality,
                    documentation: c.documentation,
                    total: c.total_score,
                    speed_ms: c.speed_ms,
                    notes: c.notes,
                    response: c.response ?? "",
                  },
                ],
        })),
    };
  })
  .sort((a, b) => b.average - a.average);

let funding = null;
if (existsSync(fundingPath)) {
  funding = JSON.parse(readFileSync(fundingPath, "utf8"));
  // mark wishlist items that already appear on the leaderboard
  const present = new Set(models.map((m) => m.id));
  funding = {
    ...funding,
    wishlist: (funding.wishlist || []).map((w) => ({
      ...w,
      status: present.has(w.model_id) ? "scored" : w.status,
    })),
  };
}

const out = {
  generated_at: raw.generated_at,
  judge: raw.judge,
  judges: raw.judges ?? (raw.judge ? String(raw.judge).split("+") : []),
  runs: raw.runs ?? 1,
  tier: raw.tier ?? null,
  models,
  funding,
};

mkdirSync(path.join(__dirname, "../data"), { recursive: true });
writeFileSync(path.join(__dirname, "../data/results.json"), JSON.stringify(out, null, 2) + "\n");
console.log(
  `wrote data/results.json (${models.length} model${models.length === 1 ? "" : "s"}: ${models
    .map((m) => m.id)
    .join(", ")})`
);
