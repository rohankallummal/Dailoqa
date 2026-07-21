"use client";

import {
  createContext,
  useContext,
  useSyncExternalStore,
  type ReactNode,
} from "react";

export type DocsLanguage = "python" | "js";

type LanguageContextValue = {
  lang: DocsLanguage;
  setLang: (lang: DocsLanguage) => void;
};

const LanguageContext = createContext<LanguageContextValue | null>(null);

const listeners = new Set<() => void>();

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

function isLanguage(value: string | null): value is DocsLanguage {
  return value === "python" || value === "js";
}

export function readStoredLanguage(storageKey: string): DocsLanguage {
  if (typeof window === "undefined") return "python";
  const stored = window.localStorage.getItem(storageKey);
  return isLanguage(stored) ? stored : "python";
}

export function LanguageProvider({
  storageKey,
  children,
}: {
  storageKey: string;
  children: ReactNode;
}) {
  const lang = useSyncExternalStore<DocsLanguage>(
    subscribe,
    () => readStoredLanguage(storageKey),
    () => "python",
  );

  const update = (next: DocsLanguage) => {
    window.localStorage.setItem(storageKey, next);
    listeners.forEach((listener) => listener());
  };

  return (
    <LanguageContext.Provider value={{ lang, setLang: update }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextValue {
  const value = useContext(LanguageContext);
  if (!value) {
    return { lang: "python", setLang: () => {} };
  }
  return value;
}
