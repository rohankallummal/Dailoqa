import type { ReactNode } from "react";
import { Sidebar } from "@/components/sidebar/Sidebar";
import { Header } from "@/components/layout/Header";
import { ChatPanelProvider } from "@/components/chat/ChatPanelProvider";
import { ChatPanel } from "@/components/chat/ChatPanel";

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
