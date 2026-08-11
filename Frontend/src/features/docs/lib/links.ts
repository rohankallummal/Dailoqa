import { docsSourceHrefs } from "./docsNavConfig";

function isExternal(href: string | undefined): boolean {
  return !!href && (href.startsWith("http://") || href.startsWith("https://"));
}

function isAnchor(href: string | undefined): boolean {
  return !!href && href.startsWith("#");
}

export function resolveDocHref(href: string | undefined): string | undefined {
  if (!href || isExternal(href) || isAnchor(href)) return undefined;

  const [path, hash] = href.split("#");
  const normalized = path.endsWith("/") ? path.slice(0, -1) : path;
  const target = docsSourceHrefs[normalized];

  if (!target) return undefined;
  return hash ? `${target}#${hash}` : target;
}

export function isDeadLink(href: string | undefined): boolean {
  if (!href) return true;
  if (isAnchor(href)) return false;
  return !resolveDocHref(href);
}
