"use client";

import { useLanguage, type DocsLanguage } from "./LanguageProvider";

const options: { label: string; value: DocsLanguage }[] = [
  { label: "Python", value: "python" },
  { label: "TypeScript", value: "js" },
];

export function LanguageToggle() {
  const { lang, setLang } = useLanguage();

  return (
    <div className="flex gap-6 border-b border-line">
      {options.map((option) => {
        const isActive = option.value === lang;
        return (
          <button
            key={option.value}
            type="button"
            onClick={() => setLang(option.value)}
            className={`relative -mb-px pb-3 text-sm font-medium transition-colors ${
              isActive ? "text-accent" : "text-ink-soft hover:text-ink"
            }`}
          >
            {option.label}
            {isActive && (
              <span className="absolute inset-x-0 bottom-0 h-0.5 rounded-full bg-accent" />
            )}
          </button>
        );
      })}
    </div>
  );
}
