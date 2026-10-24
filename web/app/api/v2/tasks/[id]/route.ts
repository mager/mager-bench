import { agentBench } from "@/lib/agent-v2";
export const dynamic = "force-static";
export function generateStaticParams() {
  return agentBench.tasks.map(({ id }) => ({ id }));
}
export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const task = agentBench.tasks.find((t) => t.id === id);
  return task
    ? Response.json(task)
    : Response.json({ error: "Task not found" }, { status: 404 });
}
