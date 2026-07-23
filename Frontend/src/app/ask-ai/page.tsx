import type { Metadata } from "next";
import { AskAiWorkspace, ChatStreamProvider } from "@/features/chat";

export const metadata: Metadata = {
  title: "Ask AI — Dailoqa",
};

export default function AskAiPage() {
  return (
    <ChatStreamProvider>
      <AskAiWorkspace />
    </ChatStreamProvider>
  );
}
