"use client";

import { Children, isValidElement, useState, type ReactElement, type ReactNode } from "react";

export function useTabbedChildren<Props>(children: ReactNode) {
  const tabs = Children.toArray(children).filter((child) =>
    isValidElement(child),
  ) as ReactElement<Props>[];
  const [active, setActive] = useState(0);

  return { tabs, current: Math.min(active, Math.max(0, tabs.length - 1)), setActive };
}
