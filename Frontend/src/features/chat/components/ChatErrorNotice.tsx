"use client";

import { AlertCircle } from "lucide-react";

export function ChatErrorNotice({ message }: { message: string }) {
  return (
    <div
      role="alert"
      className="flex flex-shrink-0 items-center justify-center gap-2 px-3 pt-3 text-sm text-ink-soft"
    >
      <AlertCircle className="h-3.5 w-3.5 flex-shrink-0 text-accent" strokeWidth={2} />
      {message}
    </div>
  );
}
