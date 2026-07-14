import { Bell } from "lucide-react";
import { AskAiButton } from "@/components/chat/AskAiButton";
import { SearchBar } from "@/components/layout/SearchBar";
import { SearchHint } from "@/components/layout/SearchHint";

export function Header() {
  return (
    <header className="flex h-16 flex-shrink-0 items-center justify-end border-b border-line bg-white px-6">
      <div className="flex items-center gap-3">
        <AskAiButton />

        <SearchBar hint={<SearchHint />} />

        <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-transparent transition-colors duration-200 hover:border-line hover:bg-hover">
          <Bell className="h-[18px] w-[18px] text-ink-soft" />
        </div>
      </div>
    </header>
  );
}
