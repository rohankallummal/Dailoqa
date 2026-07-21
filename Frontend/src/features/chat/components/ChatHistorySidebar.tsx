import { PanelLeftClose, Search } from "lucide-react";
import { ChatEmptyState } from "./ChatEmptyState";

export function ChatHistorySidebar({
  collapsed,
  onToggle,
}: {
  collapsed: boolean;
  onToggle: () => void;
}) {
  return (
    <aside
      className={`h-full shrink-0 overflow-hidden border-r border-line bg-white transition-[width] duration-300 ease-in-out motion-reduce:transition-none ${
        collapsed ? "w-0" : "w-[320px]"
      }`}
    >
      <div className="flex h-full w-[320px] flex-col">
        <div className="flex h-16 flex-shrink-0 items-center justify-between border-b border-line px-5">
          <button
            type="button"
            onClick={onToggle}
            aria-label="Collapse sidebar"
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-transparent text-ink-soft transition-colors duration-200 hover:border-line hover:bg-hover hover:text-ink"
          >
            <PanelLeftClose className="h-[18px] w-[18px]" />
          </button>
          <span className="text-[11px] font-bold uppercase tracking-[0.1em] text-ink-muted">
            Chat History
          </span>
        </div>

        <div className="p-5">
          <div className="flex items-center gap-2.5 rounded-lg border border-line bg-page px-3 py-2.5">
            <Search className="h-4 w-4 shrink-0 text-ink-muted" />
            <input
              type="text"
              placeholder="Search"
              aria-label="Search"
              className="min-w-0 flex-1 bg-transparent text-sm text-ink outline-none placeholder:text-ink-muted"
            />
          </div>

          <ChatEmptyState
            showIcon={false}
            title="No conversations yet"
            description={<>Start chatting</>}
            className="mt-8 flex flex-col items-center px-2 text-center"
          />
        </div>
      </div>
    </aside>
  );
}
