import { NextResponse } from "next/server";
import data from "@/data/counterexample.json";
export const dynamic = "force-static";
export async function GET() {
  return NextResponse.json(
    {
      benchmark_version: data.version,
      status: data.calibrationReady ? "preliminary_calibration" : "calibrating",
      scoring: "deterministic_mutation_coverage",
      unit: "exposed_faults_out_of_8",
      suite_sha256: data.suiteHash,
      generated_at: data.lastRunAt,
      faults: data.faults,
      models: data.models,
      runs: data.runs,
    },
    {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "public, max-age=300",
      },
    },
  );
}
