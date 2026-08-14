import type { ReactNode } from "react";

export function Frame({
  caption,
  children,
}: {
  caption?: string;
  children?: ReactNode;
}) {
  return (
    <figure className="my-4 overflow-hidden rounded-xl border border-line bg-white p-2 [&_img]:my-0 [&_p]:my-0">
      {children}
      {caption ? (
        <figcaption className="px-2 pb-1 pt-2 text-xs text-ink-muted">
          {caption}
        </figcaption>
      ) : null}
    </figure>
  );
}
