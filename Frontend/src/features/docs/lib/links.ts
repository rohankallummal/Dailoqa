export function isExternal(href: string | undefined): boolean {
  return !!href && (href.startsWith("http://") || href.startsWith("https://"));
}

export function isAnchor(href: string | undefined): boolean {
  return !!href && href.startsWith("#");
}

export function isDeadLink(href: string | undefined): boolean {
  if (!href) return true;
  if (isAnchor(href)) return false;
  if (isExternal(href)) return false;
  return true;
}
