"use client";

import { useSyncExternalStore } from "react";

export type DocsLanguage = "python" | "js";

export const LANGUAGE_OPTIONS: { label: string; value: DocsLanguage }[] = [
  { label: "Python", value: "python" },
  { label: "TypeScript", value: "js" },
];

const STORAGE_KEY = "docsLang";
const DEFAULT_LANGUAGE: DocsLanguage = "python";

const listeners = new Set<() => void>();

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

function readStoredLanguage(): DocsLanguage {
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return stored === "python" || stored === "js" ? stored : DEFAULT_LANGUAGE;
}

function setLang(next: DocsLanguage) {
  window.localStorage.setItem(STORAGE_KEY, next);
  listeners.forEach((listener) => listener());
}

export function useLanguage(): {
  lang: DocsLanguage;
  setLang: (lang: DocsLanguage) => void;
} {
  const lang = useSyncExternalStore(subscribe, readStoredLanguage, () => DEFAULT_LANGUAGE);
  return { lang, setLang };
}
