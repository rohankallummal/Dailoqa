"use client";

import { useState } from "react";

export function useComposer(onSend: (text: string) => void, disabled?: boolean) {
  const [value, setValue] = useState("");

  const submit = (): boolean => {
    const text = value.trim();
    if (!text || disabled) return false;
    onSend(text);
    setValue("");
    return true;
  };

  return { value, setValue, submit };
}
