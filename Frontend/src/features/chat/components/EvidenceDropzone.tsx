"use client";

import { useEffect, useRef, useState, type DragEvent } from "react";
import { Upload } from "lucide-react";

export function EvidenceDropzone({ onAdd }: { onAdd: (files: File[]) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  useEffect(() => {
    const handlePaste = (event: ClipboardEvent) => {
      const files = Array.from(event.clipboardData?.files ?? []);
      if (files.length > 0) {
        event.preventDefault();
        onAdd(files);
      }
    };
    window.addEventListener("paste", handlePaste);
    return () => window.removeEventListener("paste", handlePaste);
  }, [onAdd]);

  const handleDrop = (event: DragEvent<HTMLButtonElement>) => {
    event.preventDefault();
    setDragging(false);
    onAdd(Array.from(event.dataTransfer.files));
  };

  return (
    <>
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragEnter={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragOver={(event) => event.preventDefault()}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={`flex w-full flex-col items-center gap-2 rounded-xl border border-dashed px-4 py-5 text-center transition-colors duration-200 ${
          dragging ? "border-accent bg-active" : "border-line bg-page hover:border-accent hover:bg-active"
        }`}
      >
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-white text-accent shadow-sm">
          <Upload className="h-[18px] w-[18px]" strokeWidth={1.8} />
        </span>
        <span className="text-sm font-medium text-ink">
          <span className="text-accent">Click to browse</span> or drag files here
        </span>
        <span className="text-xs text-ink-muted">or paste a screenshot with Ctrl+V</span>
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="image/*,video/*"
        multiple
        hidden
        onChange={(event) => {
          onAdd(Array.from(event.target.files ?? []));
          event.target.value = "";
        }}
      />
    </>
  );
}
