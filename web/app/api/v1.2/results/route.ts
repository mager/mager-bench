import { archivedEveryday } from "@/lib/everyday";
export const dynamic = "force-static";
export function GET() {
  return Response.json(archivedEveryday);
}
