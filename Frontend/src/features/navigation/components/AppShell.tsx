import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { ChatPanelProvider, ChatPanel } from "@/features/chat";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <ChatPanelProvider>
      <div className="flex h-screen overflow-hidden bg-page">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <Header />
          <div className="flex min-h-0 flex-1">
            <main className="min-w-0 flex-1 overflow-y-auto">{children}</main>
            <ChatPanel />
          </div>
        </div>
      </div>
    </ChatPanelProvider>
  );
}
