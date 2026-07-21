"use client";

import { Lock, Users, Building2, type LucideIcon } from "lucide-react";

export type Visibility = "private" | "team" | "tenant";

const VISIBILITY_OPTIONS: {
  value: Visibility;
  icon: LucideIcon;
  title: string;
  subtitle: string;
}[] = [
  {
    value: "private",
    icon: Lock,
    title: "Private",
    subtitle: "Only you can access this playbook",
  },
  {
    value: "team",
    icon: Users,
    title: "Team",
    subtitle: "Specific teams can access this playbook",
  },
  {
    value: "tenant",
    icon: Building2,
    title: "Tenant",
    subtitle: "Everyone in your organization can access",
  },
];

export function AccessTab({
  visibility,
  onVisibilityChange,
}: {
  visibility: Visibility;
  onVisibilityChange: (value: Visibility) => void;
}) {
  return (
    <div className="rounded-xl border border-line bg-white p-6">
      <p className="text-xs font-semibold tracking-wide text-ink-muted">
        VISIBILITY
      </p>

      <div className="mt-4 flex flex-col gap-3">
        {VISIBILITY_OPTIONS.map((option) => {
          const Icon = option.icon;
          const selected = visibility === option.value;
          return (
            <button
              key={option.value}
              type="button"
              onClick={() => onVisibilityChange(option.value)}
              className={`flex items-start gap-3 rounded-lg border bg-white p-4 text-left transition-colors ${
                selected
                  ? "border-ink ring-1 ring-ink"
                  : "border-line hover:border-ink-muted"
              }`}
            >
              <Icon
                className="mt-0.5 h-4 w-4 flex-shrink-0 text-ink-soft"
                strokeWidth={1.9}
              />
              <span>
                <span className="block text-sm font-semibold text-ink">
                  {option.title}
                </span>
                <span className="mt-0.5 block text-xs text-ink-soft">
                  {option.subtitle}
                </span>
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
