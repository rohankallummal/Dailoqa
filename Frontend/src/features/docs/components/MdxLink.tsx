import type { ReactNode } from "react";
import Link from "next/link";
import { isDeadLink, resolveDocHref } from "../lib/links";

const linkClass =
  "font-medium text-accent underline decoration-accent/30 underline-offset-2 hover:decoration-accent";

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

  const resolved = resolveDocHref(href);
  if (resolved) {
    return (
      <Link href={resolved} className={linkClass}>
        {children}
      </Link>
    );
  }

  return (
    <a href={href} className={linkClass}>
      {children}
    </a>
  );
}
