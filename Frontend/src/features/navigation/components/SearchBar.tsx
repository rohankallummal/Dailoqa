import { Search } from "lucide-react";

export function SearchBar() {
  return (
    <div className="flex h-9 w-64 items-center gap-2 rounded-lg border border-line bg-page px-3">
      <Search className="h-4 w-4 shrink-0 text-ink-muted" />
      <input
        type="text"
        placeholder="Search…"
        aria-label="Search"
        className="min-w-0 flex-1 bg-transparent text-sm text-ink outline-none placeholder:text-ink-muted"
      />
    </div>
  );
}
