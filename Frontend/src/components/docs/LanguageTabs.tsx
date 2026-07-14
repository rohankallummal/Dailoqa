"use client";

import { useState } from "react";

const languages = ["Python", "TypeScript"];

export function LanguageTabs() {
  const [active, setActive] = useState(languages[0]);

  return (
    <div className="flex gap-6 border-b border-line">
      {languages.map((language) => {
        const isActive = language === active;
        return (
          <button
            key={language}
            type="button"
            onClick={() => setActive(language)}
            className={`relative -mb-px pb-3 text-sm font-medium transition-colors ${
              isActive ? "text-accent" : "text-ink-soft hover:text-ink"
            }`}
          >
            {language}
            {isActive && (
              <span className="absolute inset-x-0 bottom-0 h-0.5 rounded-full bg-accent" />
            )}
          </button>
        );
      })}
    </div>
  );
}
