import type { ReactNode } from "react";
import { ArrowRight } from "lucide-react";
import { Icon } from "./Icon";
import { isDeadLink, isExternal } from "./links";

export function Card({
  title,
  icon,
  href,
  arrow = false,
  cta,
  children,
}: {
  title?: string;
  icon?: string;
  href?: string;
  arrow?: boolean;
  cta?: string;
  children?: ReactNode;
}) {
  const base =
    "group flex flex-col rounded-2xl border border-line bg-white p-5 shadow-sm transition duration-200";
  const interactive =
    " hover:-translate-y-0.5 hover:border-accent/40 hover:shadow-md";

  const inner = (
    <>
      {icon ? (
        <span className="mb-3 inline-flex text-accent">
          <Icon icon={icon} size={20} />
        </span>
      ) : null}
      {title ? (
        <h3 className="text-base font-semibold text-ink">{title}</h3>
      ) : null}
      {children ? (
        <div className="mt-1.5 flex-1 text-sm leading-relaxed text-ink-soft [&_code]:text-ink [&_p]:my-0">
          {children}
        </div>
      ) : null}
      {arrow || cta ? (
        <span className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-ink-muted transition-colors group-hover:text-accent">
          {cta}
          {arrow ? <ArrowRight className="h-4 w-4" /> : null}
        </span>
      ) : null}
    </>
  );

  if (isDeadLink(href)) {
    return <div className={base}>{inner}</div>;
  }

  const external = isExternal(href);
  return (
    <a
      href={href}
      {...(external ? { target: "_blank", rel: "noreferrer" } : {})}
      className={base + interactive}
    >
      {inner}
    </a>
  );
}
