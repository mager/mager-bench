import { NextResponse } from "next/server";
import results from "@/data/results.json";

export async function GET() {
  return NextResponse.json(results, {
    headers: {
      "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
    },
  });
}
