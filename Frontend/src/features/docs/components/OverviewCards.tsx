"use client";

import { StartingPointCard } from "./StartingPointCard";
import { startingPoints } from "../lib/startingPoints";
import { useLanguage } from "./LanguageProvider";

function frameworkStorageKey(href: string): string {
  const segment = href.split("/").filter(Boolean).pop() ?? "";
  return `${segment}Lang`;
}

export function OverviewCards() {
  const { lang } = useLanguage();

  return (
    <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {startingPoints.map((point, index) => (
        <StartingPointCard
          key={point.href}
          {...point}
          onClick={() =>
            window.localStorage.setItem(frameworkStorageKey(point.href), lang)
          }
          priority={index === 0}
        />
      ))}
    </div>
  );
}
