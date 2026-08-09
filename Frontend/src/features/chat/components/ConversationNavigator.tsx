"use client";

import { useCallback, useEffect, useMemo, useRef, useState, type KeyboardEvent } from "react";
import { useConversationMap } from "../hooks/useConversationMap";
import { useMediaQuery, useReducedMotion } from "../hooks/useMediaQuery";
import { buildMarkers, MARKER_HEIGHT, MARKER_WIDTH } from "../lib/conversationMap";
import type { Message } from "../lib/messageReducer";

const HOVER_QUERY = "(hover: hover) and (pointer: fine)";
const RAIL_WIDTH = MARKER_WIDTH + 12;
const RAIL_RATIO = 0.42;
const MIN_RAIL_HEIGHT = 140;
const MAX_RAIL_HEIGHT = 260;
const PANEL_RATIO = 0.7;
const MIN_PANEL_HEIGHT = 220;
const MAX_PANEL_HEIGHT = 420;
const MIN_THUMB_HEIGHT = 10;
const ROW_PREFIX = "conversation-navigator-row";

function fit(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, Math.round(value)));
}

export function ConversationNavigator({
  scroller,
  messages,
}: {
  scroller: HTMLElement | null;
  messages: Message[];
}) {
  const reducedMotion = useReducedMotion();
  const hasHover = useMediaQuery(HOVER_QUERY);
  const { anchors, scrollHeight, clientHeight, scrollable, activeId, viewport, jumpTo } =
    useConversationMap(scroller, messages);

  const [open, setOpen] = useState(false);
  const [pinned, setPinned] = useState(false);
  const [cursorId, setCursorId] = useState<string | null>(null);

  const rootRef = useRef<HTMLDivElement>(null);
  const railRef = useRef<HTMLButtonElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  const expanded = open || pinned;
  const cursor = cursorId ?? activeId;

  const close = useCallback(() => {
    setOpen(false);
    setPinned(false);
    setCursorId(null);
  }, []);

  const [wasScrollable, setWasScrollable] = useState(scrollable);
  if (scrollable !== wasScrollable) {
    setWasScrollable(scrollable);
    if (!scrollable) close();
  }

  useEffect(() => {
    if (!expanded) return;
    const onKeyDown = (event: globalThis.KeyboardEvent) => {
      if (event.key !== "Escape") return;
      event.stopPropagation();
      close();
      railRef.current?.focus();
    };
    const onPointerDown = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) close();
    };
    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("pointerdown", onPointerDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("pointerdown", onPointerDown);
    };
  }, [expanded, close]);

  useEffect(() => {
    if (!expanded || !activeId) return;
    listRef.current?.querySelector(`[data-row="${activeId}"]`)?.scrollIntoView({ block: "nearest" });
  }, [expanded, activeId]);

  const railHeight = fit(clientHeight * RAIL_RATIO, MIN_RAIL_HEIGHT, MAX_RAIL_HEIGHT);
  const panelHeight = fit(clientHeight * PANEL_RATIO, MIN_PANEL_HEIGHT, MAX_PANEL_HEIGHT);

  const markers = useMemo(
    () => buildMarkers({ anchors, scrollHeight, railHeight, activeId }),
    [anchors, scrollHeight, railHeight, activeId],
  );

  const thumbHeight = fit(viewport.size * railHeight, MIN_THUMB_HEIGHT, railHeight);
  const thumbTop = fit(viewport.start * railHeight, 0, railHeight - thumbHeight);

  const moveCursor = (index: number) => {
    const target = anchors[Math.min(anchors.length - 1, Math.max(0, index))];
    if (!target) return;
    setCursorId(target.id);
    listRef.current?.querySelector(`[data-row="${target.id}"]`)?.scrollIntoView({ block: "nearest" });
  };

  const onListKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    const current = anchors.findIndex((anchor) => anchor.id === cursor);
    switch (event.key) {
      case "ArrowDown":
        event.preventDefault();
        moveCursor(current + 1);
        break;
      case "ArrowUp":
        event.preventDefault();
        moveCursor(current - 1);
        break;
      case "Home":
        event.preventDefault();
        moveCursor(0);
        break;
      case "End":
        event.preventDefault();
        moveCursor(anchors.length - 1);
        break;
      case "Enter":
      case " ":
        event.preventDefault();
        if (cursor) jumpTo(cursor);
        close();
        break;
      default:
        break;
    }
  };

  if (!scrollable || anchors.length === 0) return null;

  return (
    <div
      ref={rootRef}
      className="pointer-events-none absolute inset-y-0 right-0 z-20 flex items-center pr-5"
      onMouseEnter={() => hasHover && setOpen(true)}
      onMouseLeave={() => hasHover && !pinned && setOpen(false)}
    >
      {expanded && !hasHover && (
        <div
          aria-hidden="true"
          onClick={() => close()}
          className="pointer-events-auto fixed inset-0 bg-ink/10"
        />
      )}

      <div className="pointer-events-auto relative" style={{ height: railHeight, width: RAIL_WIDTH }}>
        {expanded && (
          <div
            className="absolute top-1/2 flex w-[280px] flex-col overflow-hidden rounded-xl border border-line bg-white shadow-lg"
            style={{
              right: RAIL_WIDTH,
              maxHeight: panelHeight,
              transform: "translateY(-50%)",
              animation: reducedMotion ? undefined : "conversationNavigatorIn 160ms ease-out",
            }}
          >
            <p className="flex-shrink-0 border-b border-line px-3 py-2.5 text-[11px] font-bold uppercase tracking-[0.1em] text-ink-muted">
              Jump to message
            </p>
            <div
              ref={listRef}
              role="listbox"
              tabIndex={0}
              aria-label="Jump to message"
              aria-activedescendant={cursor ? `${ROW_PREFIX}-${cursor}` : undefined}
              onKeyDown={onListKeyDown}
              className="min-h-0 flex-1 overflow-y-auto p-1.5 outline-none [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-scrollbar [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar]:w-1.5"
            >
              {anchors.map((anchor) => {
                const isActive = anchor.id === activeId;
                const isCursor = anchor.id === cursor;
                return (
                  <div
                    key={anchor.id}
                    id={`${ROW_PREFIX}-${anchor.id}`}
                    data-row={anchor.id}
                    role="option"
                    aria-selected={isActive}
                    onClick={() => {
                      jumpTo(anchor.id);
                      if (!hasHover) close();
                    }}
                    onMouseEnter={() => setCursorId(anchor.id)}
                    className={`flex cursor-pointer items-center gap-2.5 rounded-lg px-2.5 py-2 text-[13px] transition-colors duration-200 motion-reduce:transition-none ${
                      isActive
                        ? "bg-active font-medium text-accent"
                        : isCursor
                          ? "bg-hover text-ink"
                          : "text-ink-soft"
                    }`}
                  >
                    <span
                      aria-hidden="true"
                      className={`h-1.5 w-1.5 flex-shrink-0 rounded-full ${
                        anchor.role === "user" ? "bg-accent" : "bg-ink-muted"
                      } ${isActive ? "" : "opacity-70"}`}
                    />
                    <span className="min-w-0 flex-1 truncate">{anchor.preview}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <button
          ref={railRef}
          type="button"
          aria-expanded={expanded}
          aria-label={`Conversation minimap, ${anchors.length} messages`}
          onClick={() => {
            setPinned((value) => !value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          onKeyDown={(event) => {
            if (event.key !== "ArrowDown" && event.key !== "Enter") return;
            event.preventDefault();
            setOpen(true);
            setPinned(true);
            requestAnimationFrame(() => listRef.current?.focus());
          }}
          className="absolute inset-0 rounded-lg outline-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          <span
            aria-hidden="true"
            className="absolute right-0 rounded-full bg-accent/15"
            style={{ top: thumbTop, height: thumbHeight, width: MARKER_WIDTH }}
          />
          {markers.map((marker) => (
            <span
              key={marker.key}
              aria-hidden="true"
              className={`absolute right-0 rounded-full transition-[width,background-color] duration-200 motion-reduce:transition-none ${
                marker.active ? "bg-accent" : "bg-ink-muted/50"
              }`}
              style={{
                top: marker.top,
                height: MARKER_HEIGHT,
                width: marker.active ? MARKER_WIDTH : MARKER_WIDTH - 4,
              }}
            />
          ))}
        </button>
      </div>
    </div>
  );
}
