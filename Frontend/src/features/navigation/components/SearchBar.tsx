import { Search } from "lucide-react";
import type { ReactNode, Ref } from "react";

type SearchBarProps = {
  inputRef?: Ref<HTMLInputElement>;
  value?: string;
  onValueChange?: (value: string) => void;
  className?: string;
  placeholder?: string;
  hint?: ReactNode;
};

export function SearchBar({
  inputRef,
  value,
  onValueChange,
  className = "flex h-9 w-64 items-center gap-2 rounded-lg border border-line bg-page px-3",
  placeholder = "Search…",
  hint,
}: SearchBarProps) {
  return (
    <div className={className}>
      <Search className="h-4 w-4 shrink-0 text-ink-muted" />
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={
          onValueChange ? (event) => onValueChange(event.target.value) : undefined
        }
        placeholder={placeholder}
        aria-label="Search"
        className="min-w-0 flex-1 bg-transparent text-sm text-ink outline-none placeholder:text-ink-muted"
      />
      {hint}
    </div>
  );
}
