import { agentBench } from "@/lib/agent-v2";
export const dynamic = "force-static";
export function GET() {
  return Response.json(agentBench);
}
