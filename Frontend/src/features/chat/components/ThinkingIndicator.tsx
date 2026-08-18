"use client";

import { useEffect, useRef } from "react";
import lottie from "lottie-web/build/player/lottie_light";
import { useReducedMotion } from "../hooks/useMediaQuery";

export function ThinkingIndicator({ label }: { label?: string | null }) {
  const reducedMotion = useReducedMotion();
  const host = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!host.current) return;
    const animation = lottie.loadAnimation({
      container: host.current,
      renderer: "svg",
      loop: true,
      autoplay: !reducedMotion,
      path: "/loading.json",
    });
    return () => animation.destroy();
  }, [reducedMotion]);

  return (
    <div className="flex justify-start">
      <div
        role="status"
        aria-label={label ?? "The assistant is thinking"}
        className="flex items-center gap-1.5"
      >
        <span ref={host} aria-hidden="true" className="h-16 w-20 flex-shrink-0" />
        {label ? <span className="text-xs text-ink-muted">{label}…</span> : null}
      </div>
    </div>
  );
}
