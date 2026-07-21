import type { Metadata } from "next";
import { AskAiWorkspace } from "@/features/chat";

export const metadata: Metadata = {
  title: "Ask AI — Dailoqa",
};

export default function AskAiPage() {
  return <AskAiWorkspace />;
}
