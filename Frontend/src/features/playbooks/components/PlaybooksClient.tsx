"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { ChevronDown, Plus, Search, Tag } from "lucide-react";
import type { Playbook } from "../types";
import { PlaybookCard } from "./PlaybookCard";

function Toolbar({
  query,
  onQueryChange,
}: {
  query: string;
  onQueryChange: (value: string) => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="relative min-w-[240px] flex-1">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-muted" />
        <input
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="Search playbooks…"
          className="w-full rounded-lg border border-line bg-white py-2 pl-9 pr-3 text-sm text-ink outline-none transition-colors focus:border-accent placeholder:text-ink-muted"
        />
      </div>

      <FilterButton label="Type" />
      <FilterButton label="Status" />
      <FilterButton label="Tags" icon={<Tag className="h-4 w-4 text-ink-muted" />} />
      <FilterButton label="Newest first" icon={<ChevronDown className="h-4 w-4 text-ink-muted" />} trailingIcon />
    </div>
  );
}

function FilterButton({
  label,
  icon,
  trailingIcon,
}: {
  label: string;
  icon?: React.ReactNode;
  trailingIcon?: boolean;
}) {
  return (
    <button
      type="button"
      className="flex items-center gap-2 rounded-lg border border-line bg-white px-3 py-2 text-sm text-ink-soft transition-colors duration-200 hover:bg-hover"
    >
      {!trailingIcon && icon}
      {label}
      {trailingIcon ? icon : <ChevronDown className="h-4 w-4 text-ink-muted" />}
    </button>
  );
}

export function PlaybooksClient() {
  const [playbooks] = useState<Playbook[]>([]);
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return playbooks;
    return playbooks.filter(
      (playbook) =>
        playbook.name.toLowerCase().includes(q) ||
        playbook.description.toLowerCase().includes(q) ||
        playbook.tag?.label.toLowerCase().includes(q),
    );
  }, [playbooks, query]);

  return (
    <div className="px-8 py-7">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Playbooks</h1>
          <p className="mt-1 text-sm text-ink-soft">Orchestrated AI workflows</p>
        </div>
        <Link
          href="/playbooks/create"
          className="flex flex-shrink-0 items-center gap-2 rounded-lg bg-ink px-4 py-2.5 text-sm font-medium text-white transition-opacity duration-200 hover:opacity-90"
        >
          <Plus className="h-4 w-4" strokeWidth={2} />
          New Playbook
        </Link>
      </div>

      <div className="mt-6">
        <Toolbar query={query} onQueryChange={setQuery} />
      </div>

      {filtered.length > 0 ? (
        <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((playbook) => (
            <PlaybookCard key={playbook.id} playbook={playbook} />
          ))}
        </div>
      ) : (
        <div className="mt-16 text-center text-sm text-ink-muted">
          {query ? `No playbooks match “${query}”.` : "No playbooks yet."}
        </div>
      )}
    </div>
  );
}
