import type { Metadata } from "next";
import { AskAiWorkspace, ChatStreamProvider } from "@/features/chat";
import { NotificationsListener } from "@/features/notifications";
import { ToastProvider } from "@/shared/ui";

export const metadata: Metadata = {
  title: "Ask AI — Dailoqa",
};

export default function AskAiPage() {
  return (
    <ChatStreamProvider>
      <ToastProvider>
        <NotificationsListener />
        <AskAiWorkspace />
      </ToastProvider>
    </ChatStreamProvider>
  );
}
