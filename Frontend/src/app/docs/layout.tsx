import type { ReactNode } from "react";
import {
  DocsHeader,
  DocsNav,
  DocsSideNav,
  LanguageProvider,
} from "@/features/docs";

export default function DocsLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-page">
      <DocsHeader />
      <DocsNav />
      <LanguageProvider storageKey="docsLang">
        <div className="flex min-h-0 flex-1">
          <DocsSideNav />
          <main className="min-w-0 flex-1">{children}</main>
        </div>
      </LanguageProvider>
    </div>
  );
}
