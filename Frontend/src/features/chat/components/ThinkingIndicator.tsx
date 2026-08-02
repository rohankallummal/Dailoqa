"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import type { AnimationItem } from "lottie-web";

const ANIMATION_PATH = "/animation/thinking.json";
const ANIMATION_WIDTH = 64;
const ANIMATION_ASPECT = 800 / 600;
const REDUCED_MOTION_QUERY = "(prefers-reduced-motion: reduce)";

function subscribeToReducedMotion(onChange: () => void) {
  const query = window.matchMedia(REDUCED_MOTION_QUERY);
  query.addEventListener("change", onChange);
  return () => query.removeEventListener("change", onChange);
}

function useReducedMotion() {
  return useSyncExternalStore(
    subscribeToReducedMotion,
    () => window.matchMedia(REDUCED_MOTION_QUERY).matches,
    () => false,
  );
}

export function ThinkingIndicator() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [failed, setFailed] = useState(false);
  const reducedMotion = useReducedMotion();
  const showStatic = reducedMotion || failed;

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let animation: AnimationItem | null = null;
    let cancelled = false;

    void import("lottie-web/build/player/lottie_light")
      .then((player) => {
        if (cancelled) return;
        animation = player.default.loadAnimation({
          container,
          renderer: "svg",
          loop: true,
          autoplay: true,
          path: ANIMATION_PATH,
        });
      })
      .catch(() => {
        if (!cancelled) setFailed(true);
      });

    return () => {
      cancelled = true;
      animation?.destroy();
    };
  }, [showStatic]);

  return (
    <div className="flex justify-start">
      <div role="status" aria-label="The assistant is thinking" className="flex items-center">
        {showStatic ? (
          <span className="text-sm text-ink-muted">Thinking…</span>
        ) : (
          <div
            ref={containerRef}
            aria-hidden="true"
            style={{ width: ANIMATION_WIDTH, height: Math.round(ANIMATION_WIDTH / ANIMATION_ASPECT) }}
          />
        )}
      </div>
    </div>
  );
}
