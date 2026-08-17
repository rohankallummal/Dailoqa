"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { derivePreview, resolveActiveId, type MessageAnchor } from "../lib/conversationMap";
import type { Message } from "../lib/messageReducer";
import { useReducedMotion } from "./useMediaQuery";

const READING_LINE = 0.33;
const BOTTOM_EPSILON = 4;
const OVERFLOW_EPSILON = 24;
const SETTLE_IDLE_MS = 120;
const SETTLE_INITIAL_MS = 250;
const SETTLE_CAP_MS = 1500;

type Geometry = {
  anchors: MessageAnchor[];
  scrollHeight: number;
  clientHeight: number;
};

const EMPTY_GEOMETRY: Geometry = { anchors: [], scrollHeight: 0, clientHeight: 0 };

function sameAnchors(left: MessageAnchor[], right: MessageAnchor[]) {
  return (
    left.length === right.length &&
    left.every(
      (anchor, index) =>
        anchor.id === right[index].id &&
        anchor.top === right[index].top &&
        anchor.preview === right[index].preview,
    )
  );
}

function whenScrollSettles(element: HTMLElement, done: () => void) {
  let idle: ReturnType<typeof setTimeout>;
  let finished = false;

  const finish = () => {
    if (finished) return;
    finished = true;
    clearTimeout(idle);
    clearTimeout(cap);
    element.removeEventListener("scroll", bump);
    element.removeEventListener("scrollend", finish);
    done();
  };

  const bump = () => {
    clearTimeout(idle);
    idle = setTimeout(finish, SETTLE_IDLE_MS);
  };

  const cap = setTimeout(finish, SETTLE_CAP_MS);
  idle = setTimeout(finish, SETTLE_INITIAL_MS);
  element.addEventListener("scrollend", finish);
  element.addEventListener("scroll", bump);
}

export function useConversationMap(scroller: HTMLElement | null, messages: Message[]) {
  const reducedMotion = useReducedMotion();
  const [geometry, setGeometry] = useState<Geometry>(EMPTY_GEOMETRY);
  const [activeId, setActiveId] = useState<string | null>(null);

  const messagesRef = useRef(messages);
  const anchorsRef = useRef<MessageAnchor[]>(EMPTY_GEOMETRY.anchors);
  const suppressed = useRef(false);
  const frame = useRef(0);

  const [measuredScroller, setMeasuredScroller] = useState(scroller);
  if (scroller !== measuredScroller) {
    setMeasuredScroller(scroller);
    setGeometry(EMPTY_GEOMETRY);
    setActiveId(null);
  }

  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  const sync = useCallback(() => {
    if (!scroller || suppressed.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scroller;
    const atBottom = scrollTop >= Math.max(1, scrollHeight - clientHeight) - BOTTOM_EPSILON;
    setActiveId(resolveActiveId(anchorsRef.current, scrollTop + clientHeight * READING_LINE, atBottom));
  }, [scroller]);

  const measure = useCallback(() => {
    if (!scroller) return;
    const byId = new Map(messagesRef.current.map((message) => [message.id, message]));
    const origin = scroller.getBoundingClientRect().top - scroller.scrollTop;
    const anchors: MessageAnchor[] = [];

    scroller.querySelectorAll<HTMLElement>("[data-message-id]").forEach((node) => {
      const message = byId.get(node.dataset.messageId ?? "");
      if (message?.role !== "user") return;
      anchors.push({
        id: message.id,
        preview: derivePreview(message.content),
        top: Math.max(0, Math.round(node.getBoundingClientRect().top - origin)),
      });
    });

    anchorsRef.current = anchors;
    const { scrollHeight, clientHeight } = scroller;
    setGeometry((previous) =>
      previous.scrollHeight === scrollHeight &&
      previous.clientHeight === clientHeight &&
      sameAnchors(previous.anchors, anchors)
        ? previous
        : { anchors, scrollHeight, clientHeight },
    );
    sync();
  }, [scroller, sync]);

  const scheduleMeasure = useCallback(() => {
    if (frame.current) return;
    frame.current = requestAnimationFrame(() => {
      frame.current = 0;
      measure();
    });
  }, [measure]);

  useEffect(() => {
    if (!scroller) return;
    const observer = new ResizeObserver(scheduleMeasure);
    observer.observe(scroller);
    const content = scroller.firstElementChild;
    if (content) observer.observe(content);
    scheduleMeasure();
    return () => {
      observer.disconnect();
      cancelAnimationFrame(frame.current);
      frame.current = 0;
    };
  }, [scroller, scheduleMeasure]);

  useEffect(() => {
    scheduleMeasure();
  }, [messages.length, scheduleMeasure]);

  useEffect(() => {
    if (!scroller) return;
    let ticking = false;
    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        ticking = false;
        sync();
      });
    };
    scroller.addEventListener("scroll", onScroll, { passive: true });
    return () => scroller.removeEventListener("scroll", onScroll);
  }, [scroller, sync]);

  const jumpTo = useCallback(
    (id: string) => {
      if (!scroller) return;
      const anchor = anchorsRef.current.find((item) => item.id === id);
      if (!anchor) return;

      suppressed.current = true;
      setActiveId(id);

      const limit = Math.max(0, scroller.scrollHeight - scroller.clientHeight);
      const top = Math.min(limit, Math.max(0, anchor.top - scroller.clientHeight * READING_LINE));
      scroller.scrollTo({ top, behavior: reducedMotion ? "auto" : "smooth" });
      scroller
        .querySelector<HTMLElement>(`[data-message-id="${CSS.escape(id)}"]`)
        ?.focus({ preventScroll: true });

      whenScrollSettles(scroller, () => {
        suppressed.current = false;
        sync();
      });
    },
    [scroller, reducedMotion, sync],
  );

  return {
    anchors: geometry.anchors,
    clientHeight: geometry.clientHeight,
    scrollable: geometry.scrollHeight - geometry.clientHeight > OVERFLOW_EPSILON,
    activeId,
    jumpTo,
  };
}
