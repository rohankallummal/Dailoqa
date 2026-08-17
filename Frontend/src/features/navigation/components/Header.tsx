import { AskAiButton } from "@/features/chat";
import { NotificationBell } from "@/features/notifications";
import { SearchBar } from "./SearchBar";

export function Header() {
  return (
    <header className="flex h-16 flex-shrink-0 items-center justify-end border-b border-line bg-white px-6">
      <div className="flex items-center gap-3">
        <AskAiButton />

        <SearchBar />

        <NotificationBell />
      </div>
    </header>
  );
}
