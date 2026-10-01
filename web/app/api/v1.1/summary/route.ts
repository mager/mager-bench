import { NextResponse } from "next/server";
import data from "@/data/counterexample.json";
export const dynamic = "force-static";
export async function GET() {
  return NextResponse.json(
    {
      benchmark_version: data.version,
      status: data.calibrationReady ? "preliminary_calibration" : "calibrating",
      generated_at: data.lastRunAt,
      suite_sha256: data.suiteHash,
      total_faults: data.faults.length,
      models: data.models.map(
        ({ id, name, effort, attempts, completed, failed, scores }) => ({
          id,
          name,
          effort,
          attempts,
          completed,
          failed,
          scores,
        }),
      ),
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
