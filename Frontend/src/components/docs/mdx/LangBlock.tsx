"use client";

import type { ReactNode } from "react";
import { useLanguage, type DocsLanguage } from "./LanguageProvider";

export function LangBlock({
  lang,
  children,
}: {
  lang: DocsLanguage;
  children: ReactNode;
}) {
  const { lang: active } = useLanguage();
  if (active !== lang) return null;
  return <>{children}</>;
}
