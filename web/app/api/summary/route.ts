import { NextResponse } from "next/server";
import results from "@/data/results.json";
import challenges from "@/data/challenges.json";

// A small public feed for widgets, without the full responses in /api/results.
export async function GET() {
  const leader = [...results.models].sort((a, b) => b.average - a.average)[0];

  return NextResponse.json(
    {
      benchmark_version: "legacy-thirteen-task",
      status: "archived",
      unit: "llm_judged_score_out_of_10",
      archive_url: "https://bench.mager.co/archive/subscription",
      current_results_url: "https://bench.mager.co/api/v1.1/results",
      generated_at: results.generated_at,
      judge: results.judge,
      model_count: results.models.length,
      challenge_count: challenges.length,
      leader: leader
        ? {
            id: leader.id,
            name: leader.name,
            average: leader.average,
            challenge_count: leader.challenges.length,
          }
        : null,
    },
    {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Cache-Control":
          "public, max-age=0, s-maxage=300, stale-while-revalidate=60",
      },
    },
  );
}
