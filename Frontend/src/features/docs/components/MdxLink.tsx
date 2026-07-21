import type { ReactNode } from "react";
import { isDeadLink, isExternal } from "../lib/links";

export function MdxLink({
  href,
  children,
}: {
  href?: string;
  children?: ReactNode;
}) {
  if (isDeadLink(href)) {
    return <span>{children}</span>;
  }
  if (isExternal(href)) {
    return (
      <a
        href={href}
        target="_blank"
        rel="noreferrer"
        className="font-medium text-accent underline decoration-accent/30 underline-offset-2 hover:decoration-accent"
      >
        {children}
      </a>
    );
  }
  return (
    <a
      href={href}
      className="font-medium text-accent underline decoration-accent/30 underline-offset-2 hover:decoration-accent"
    >
      {children}
    </a>
  );
}
