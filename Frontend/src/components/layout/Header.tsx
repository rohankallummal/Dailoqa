import { Search, Bell } from "lucide-react";
import { AskAiButton } from "@/components/chat/AskAiButton";

export function Header() {
  return (
    <header className="flex h-16 flex-shrink-0 items-center justify-end border-b border-line bg-white px-6">
      <div className="flex items-center gap-3">
        <AskAiButton />

        <div className="flex h-9 w-64 items-center gap-2 rounded-lg border border-line bg-page px-3">
          <Search className="h-4 w-4 shrink-0 text-ink-muted" />
          <input
            type="text"
            placeholder="Search…"
            aria-label="Search"
            className="min-w-0 flex-1 bg-transparent text-sm text-ink outline-none placeholder:text-ink-muted"
          />
        </div>

        <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-transparent transition-colors duration-200 hover:border-line hover:bg-hover">
          <Bell className="h-[18px] w-[18px] text-ink-soft" />
        </div>
      </div>
    </header>
  );
}
