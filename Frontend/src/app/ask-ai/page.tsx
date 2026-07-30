import type { Metadata } from "next";
import { AskAiWorkspace, ChatStreamProvider } from "@/features/chat";
import { NotificationsListener } from "@/features/notifications";
import { ToastProvider } from "@/shared/ui";

export const metadata: Metadata = {
  title: "Ask AI — Dailoqa",
};

export default async function AskAiPage({
  searchParams,
}: {
  searchParams: Promise<{ conversation?: string }>;
}) {
  const { conversation } = await searchParams;
  return (
    <ChatStreamProvider>
      <ToastProvider>
        <NotificationsListener />
        <AskAiWorkspace initialConversationId={conversation} />
      </ToastProvider>
    </ChatStreamProvider>
  );
}
