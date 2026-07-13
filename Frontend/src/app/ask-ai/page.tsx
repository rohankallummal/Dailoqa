import type { Metadata } from "next";
import { AskAiWorkspace } from "@/components/chat/AskAiWorkspace";

export const metadata: Metadata = {
  title: "Ask AI — Dailoqa",
};

export default function AskAiPage() {
  return <AskAiWorkspace />;
}
