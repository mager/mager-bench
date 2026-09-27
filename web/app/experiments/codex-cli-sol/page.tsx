import { permanentRedirect } from "next/navigation";
import { modelHref } from "@/lib/model-path";

export default function CodexCLIExperiment() {
  permanentRedirect(modelHref("codex-cli/gpt-5.6-sol"));
}
