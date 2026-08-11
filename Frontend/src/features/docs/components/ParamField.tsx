import type { ReactNode } from "react";

export function ParamField({
  body,
  path,
  type,
  default: defaultValue,
  required = false,
  deprecated = false,
  children,
}: {
  body?: string;
  path?: string;
  type?: string;
  default?: string;
  required?: boolean;
  deprecated?: boolean;
  children?: ReactNode;
}) {
  const name = body ?? path;

  return (
    <div className="border-t border-line py-4 first:border-t-0">
      <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
        {name ? (
          <code className="font-mono text-sm font-semibold text-ink">
            {name}
          </code>
        ) : null}
        {type ? (
          <span className="font-mono text-xs text-ink-muted">{type}</span>
        ) : null}
        {required ? (
          <span className="rounded px-1.5 py-0.5 text-[11px] font-medium uppercase tracking-wide text-accent">
            required
          </span>
        ) : null}
        {deprecated ? (
          <span className="rounded px-1.5 py-0.5 text-[11px] font-medium uppercase tracking-wide text-amber-600">
            deprecated
          </span>
        ) : null}
        {defaultValue ? (
          <span className="font-mono text-xs text-ink-muted">
            default: {defaultValue}
          </span>
        ) : null}
      </div>
      {children ? (
        <div className="mt-2 text-sm leading-relaxed text-ink-soft [&_p:first-child]:mt-0 [&_p:last-child]:mb-0">
          {children}
        </div>
      ) : null}
    </div>
  );
}
