"use client";

import { useState } from "react";
import { Check, ChevronDown } from "lucide-react";
import { LANGUAGE_OPTIONS, useLanguage } from "../lib/language";

export function LanguageSelect() {
  const { lang, setLang } = useLanguage();
  const [open, setOpen] = useState(false);
  const selected =
    LANGUAGE_OPTIONS.find((option) => option.value === lang) ?? LANGUAGE_OPTIONS[0];

  return (
    <div className="px-3">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        className="flex w-full items-center justify-between rounded-lg border border-line bg-white px-3 py-2 text-sm font-medium text-ink transition-colors hover:border-accent/40"
      >
        {selected.label}
        <ChevronDown
          className={`h-4 w-4 text-ink-muted transition-transform ${
            open ? "rotate-180" : ""
          }`}
        />
      </button>
      {open ? (
        <ul className="mt-1 overflow-hidden rounded-lg border border-line bg-white py-1">
          {LANGUAGE_OPTIONS.map((option) => {
            const active = option.value === lang;
            return (
              <li key={option.value}>
                <button
                  type="button"
                  onClick={() => {
                    setLang(option.value);
                    setOpen(false);
                  }}
                  className={`flex w-full items-center justify-between px-3 py-1.5 text-sm transition-colors ${
                    active
                      ? "text-accent"
                      : "text-ink-soft hover:bg-page hover:text-ink"
                  }`}
                >
                  {option.label}
                  {active ? <Check className="h-3.5 w-3.5" /> : null}
                </button>
              </li>
            );
          })}
        </ul>
      ) : null}
    </div>
  );
}
