import { NextResponse } from "next/server";
import results from "@/data/results.json";

export async function GET() {
  return NextResponse.json(
    {
      ...results,
      benchmark_version: "legacy-thirteen-task",
      status: "archived",
      unit: "llm_judged_score_out_of_10",
      current_results_url: "https://bench.mager.co/api/v1.1/results",
    },
    {
      headers: {
        "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
      },
    },
  );
}
