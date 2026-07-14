"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

export type DocsLanguage = "python" | "js";

type LanguageContextValue = {
  lang: DocsLanguage;
  setLang: (lang: DocsLanguage) => void;
};

const LanguageContext = createContext<LanguageContextValue | null>(null);

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
  const [lang, setLang] = useState<DocsLanguage>("python");

  useEffect(() => {
    setLang(readStoredLanguage(storageKey));
  }, [storageKey]);

  const update = (next: DocsLanguage) => {
    setLang(next);
    window.localStorage.setItem(storageKey, next);
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
