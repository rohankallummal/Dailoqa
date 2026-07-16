"use client";

import { useState } from "react";
import { Check, X, type LucideIcon } from "lucide-react";
import type { ResourceOption } from "./resourceData";

export function ResourcePicker({
  label,
  required,
  description,
  icon: Icon,
  buttonLabel,
  options,
  selectedIds,
  onChange,
}: {
  label: string;
  required?: boolean;
  description: string;
  icon: LucideIcon;
  buttonLabel: string;
  options: ResourceOption[];
  selectedIds: string[];
  onChange: (ids: string[]) => void;
}) {
  const [open, setOpen] = useState(false);
  const selected = options.filter((option) => selectedIds.includes(option.id));

  function toggle(id: string) {
    onChange(
      selectedIds.includes(id)
        ? selectedIds.filter((existing) => existing !== id)
        : [...selectedIds, id],
    );
  }

  function remove(id: string) {
    onChange(selectedIds.filter((existing) => existing !== id));
  }

  return (
    <div className="rounded-xl border border-line bg-white p-6">
      <p className="text-xs font-semibold tracking-wide text-ink-muted">
        {label}
        {required && <span className="ml-0.5 text-amber-500">*</span>}
      </p>
      <p className="mt-2 text-sm text-ink-soft">{description}</p>

      <div className="relative mt-4 inline-block">
        <button
          type="button"
          onClick={() => setOpen((value) => !value)}
          className="flex items-center gap-2 rounded-lg border border-line bg-white px-3 py-2 text-sm font-medium text-ink transition-colors duration-200 hover:bg-hover"
        >
          <Icon className="h-4 w-4 text-ink-soft" strokeWidth={1.9} />
          {buttonLabel}
        </button>

        {open && (
          <>
            <button
              type="button"
              aria-hidden
              tabIndex={-1}
              onClick={() => setOpen(false)}
              className="fixed inset-0 z-10 cursor-default"
            />
            <div className="absolute left-0 top-full z-20 mt-1 w-72 overflow-hidden rounded-lg border border-line bg-white shadow-lg">
              {options.map((option) => {
                const isSelected = selectedIds.includes(option.id);
                return (
                  <button
                    key={option.id}
                    type="button"
                    onClick={() => toggle(option.id)}
                    className="flex w-full items-start justify-between gap-3 px-3 py-2.5 text-left text-sm transition-colors hover:bg-hover"
                  >
                    <span>
                      <span className="block font-medium text-ink">
                        {option.name}
                      </span>
                      {option.description && (
                        <span className="mt-0.5 block text-xs text-ink-muted">
                          {option.description}
                        </span>
                      )}
                    </span>
                    {isSelected && (
                      <Check className="mt-0.5 h-4 w-4 flex-shrink-0 text-accent" />
                    )}
                  </button>
                );
              })}
            </div>
          </>
        )}
      </div>

      {selected.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {selected.map((option) => (
            <span
              key={option.id}
              className="inline-flex items-center gap-1.5 rounded-full bg-hover px-2.5 py-1 text-xs font-medium text-ink"
            >
              {option.name}
              <button
                type="button"
                onClick={() => remove(option.id)}
                aria-label={`Remove ${option.name}`}
                className="text-ink-muted transition-colors hover:text-ink"
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
