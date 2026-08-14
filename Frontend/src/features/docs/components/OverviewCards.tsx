"use client";

import { StartingPointCard } from "./StartingPointCard";
import { startingPoints } from "../lib/startingPoints";

export function OverviewCards() {
  return (
    <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {startingPoints.map((point, index) => (
        <StartingPointCard
          key={point.href}
          {...point}
          priority={index === 0}
        />
      ))}
    </div>
  );
}
