"use client";

import { useEffect, useRef, useState } from "react";
import { SearchBar } from "./SearchBar";

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen((previous) => !previous);
      } else if (event.key === "Escape") {
        setOpen(false);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  useEffect(() => {
    if (!open) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    inputRef.current?.focus();
    inputRef.current?.select();
    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [open]);

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Command palette"
      onMouseDown={() => setOpen(false)}
      className="fixed inset-0 z-50 flex items-start justify-center"
    >
      <div
        aria-hidden
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        style={{ animation: "commandPaletteOverlayIn 150ms ease-out" }}
      />

      <div
        className="relative mt-[15vh] w-full max-w-xl px-4"
        style={{ animation: "commandPalettePanelIn 200ms ease-out" }}
      >
        <div onMouseDown={(event) => event.stopPropagation()}>
          <SearchBar
            inputRef={inputRef}
            value={value}
            onValueChange={setValue}
            placeholder="Search…"
            className="flex h-12 w-full items-center gap-3 rounded-xl border border-line bg-white px-4 shadow-lg"
          />
        </div>
      </div>
    </div>
  );
}
